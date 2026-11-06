#!/usr/bin/env python3
"""Tests des mutations et de l'auto-sauvegarde de LibraryService.

Execution depuis le repertoire agent/ :
    PYTHONPATH=build python3 tests/test_service.py

ou simplement :
    python3 tests/test_service.py

Le script ajoute automatiquement agent/build a sys.path (via gui.service).
Il ne modifie jamais agent/data : chaque test utilise un repertoire temporaire.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import traceback
from collections.abc import Callable
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[1]
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from gui import service as service_module  # noqa: E402
from gui.service import LibraryError, LibraryService  # noqa: E402

if service_module._cpp is None:
    print("ERREUR : impossible d'importer bibliotheque_cpp.")
    print("Compilez d'abord le module :")
    print(f"  cmake -S {AGENT_DIR} -B {AGENT_DIR / 'build'}")
    print(f"  cmake --build {AGENT_DIR / 'build'}")
    sys.exit(1)


REPO_DATA_DIR = AGENT_DIR / "data"
REPO_DATA_FILES = ("books.txt", "users.txt")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_repo_data() -> dict[str, str]:
    return {
        name: digest(REPO_DATA_DIR / name)
        for name in REPO_DATA_FILES
        if (REPO_DATA_DIR / name).exists()
    }


REPO_DATA_BEFORE = snapshot_repo_data()


def expect_error(action: Callable[[], object], expected: str) -> str:
    try:
        action()
    except LibraryError as exc:
        message = str(exc)
        assert expected in message, (
            f"message inattendu : {message!r} "
            f"(fragment attendu : {expected!r})"
        )
        return message
    raise AssertionError(
        f"LibraryError attendu (fragment {expected!r})"
    )


def test_add_book_and_persistence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = LibraryService(Path(tmp))
        assert service.get_stats().total_books == 0

        book = service.add_book(
            "Le Petit Prince",
            "Antoine de Saint-Exupéry",
            "ISBN-1",
        )
        assert book.title == "Le Petit Prince"
        assert book.isbn == "ISBN-1"
        assert book.available is True

        stats = service.get_stats()
        assert stats.total_books == 1
        assert stats.available_books == 1
        assert stats.checked_out_books == 0
        assert service.load_error is None

        # L'auto-sauvegarde a ecrit le fichier immediatement.
        books_path = Path(tmp) / "books.txt"
        assert books_path.exists()
        assert "Le Petit Prince|Antoine de Saint-Exupéry|ISBN-1|1|" in (
            books_path.read_text(encoding="utf-8").splitlines()
        )

        # Une nouvelle instance relit le livre depuis le disque.
        reloaded = LibraryService(Path(tmp))
        assert reloaded.get_stats().total_books == 1
        assert reloaded.get_books()[0].title == "Le Petit Prince"

        # Les champs sont nettoyes (espaces superflus).
        reloaded.add_book("  Titre  ", "  Auteur  ", "  ISBN-2  ")
        stored = {
            book.isbn: book for book in reloaded.get_books()
        }
        assert stored["ISBN-2"].title == "Titre"
        assert stored["ISBN-2"].author == "Auteur"


def test_add_book_validation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = LibraryService(Path(tmp))

        expect_error(
            lambda: service.add_book("", "Auteur", "ISBN-1"),
            "obligatoire",
        )
        expect_error(
            lambda: service.add_book("Titre", "   ", "ISBN-1"),
            "obligatoire",
        )
        expect_error(
            lambda: service.add_book("Titre", "Auteur", ""),
            "obligatoire",
        )
        expect_error(
            lambda: service.add_book("Titre|corrompu", "Auteur", "ISBN-1"),
            "ne peut pas contenir",
        )
        expect_error(
            lambda: service.add_book("Titre", "Auteur", "ISBN\n2"),
            "ne peut pas contenir",
        )

        service.add_book("Titre", "Auteur", "ISBN-1")
        expect_error(
            lambda: service.add_book("Autre", "Auteur", "ISBN-1"),
            "existe déjà",
        )
        assert service.get_stats().total_books == 1


def test_add_user_and_persistence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = LibraryService(Path(tmp))

        expect_error(
            lambda: service.add_user("", "USR-1"),
            "obligatoire",
        )
        expect_error(
            lambda: service.add_user("Alice", ""),
            "obligatoire",
        )

        user = service.add_user("Alice", "USR-1")
        assert user.name == "Alice"
        assert user.user_id == "USR-1"
        assert service.get_stats().users == 1

        expect_error(
            lambda: service.add_user("Bob", "USR-1"),
            "existe déjà",
        )

        users_path = Path(tmp) / "users.txt"
        assert "Alice|USR-1|" in users_path.read_text(
            encoding="utf-8"
        ).splitlines()

        reloaded = LibraryService(Path(tmp))
        assert reloaded.get_stats().users == 1
        assert reloaded.get_users()[0].name == "Alice"


def test_remove_book_rules() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = LibraryService(Path(tmp))

        expect_error(
            lambda: service.remove_book("ISBN-INCONNU"),
            "Aucun livre",
        )

        service.add_book("Livre", "Auteur", "ISBN-1")
        service.add_user("Alice", "USR-1")
        service.checkout_book("ISBN-1", "USR-1")

        # Regle critique : impossible de supprimer un livre emprunte.
        expect_error(
            lambda: service.remove_book("ISBN-1"),
            "en cours d'emprunt",
        )
        assert service.get_stats().total_books == 1
        assert service.get_books()[0].available is False

        # Apres le retour, la suppression est autorisee.
        service.return_book("ISBN-1")
        service.remove_book("ISBN-1")
        assert service.get_stats().total_books == 0

        books_path = Path(tmp) / "books.txt"
        assert "ISBN-1" not in books_path.read_text(encoding="utf-8")

        reloaded = LibraryService(Path(tmp))
        assert reloaded.get_stats().total_books == 0


def test_checkout_and_return() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = LibraryService(Path(tmp))
        service.add_book("Livre", "Auteur", "ISBN-1")
        service.add_user("Alice", "USR-1")

        expect_error(
            lambda: service.checkout_book("ISBN-INCONNU", "USR-1"),
            "Aucun livre",
        )
        expect_error(
            lambda: service.checkout_book("ISBN-1", "USR-INCONNU"),
            "Aucun adhérent",
        )
        expect_error(
            lambda: service.checkout_book("", "USR-1"),
            "obligatoire",
        )

        service.checkout_book("ISBN-1", "USR-1")
        stats = service.get_stats()
        assert stats.available_books == 0
        assert stats.checked_out_books == 1

        book = service.get_books()[0]
        assert book.available is False
        assert book.borrower_id == "USR-1"
        user = service.get_users()[0]
        assert user.borrowed_books == ("ISBN-1",)

        # Un livre deja emprunte ne peut pas etre emprunte a nouveau.
        expect_error(
            lambda: service.checkout_book("ISBN-1", "USR-1"),
            "déjà emprunté",
        )

        # La persistance conserve l'emprunt.
        reloaded = LibraryService(Path(tmp))
        reloaded_book = reloaded.get_books()[0]
        assert reloaded_book.available is False
        assert reloaded_book.borrower_id == "USR-1"

        service.return_book("ISBN-1")
        stats = service.get_stats()
        assert stats.available_books == 1
        assert stats.checked_out_books == 0
        assert service.get_users()[0].borrowed_books == ()

        expect_error(
            lambda: service.return_book("ISBN-1"),
            "n'est pas en cours d'emprunt",
        )
        expect_error(
            lambda: service.return_book("ISBN-INCONNU"),
            "Aucun livre",
        )


def test_backup() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service = LibraryService(Path(tmp))

        # Aucun fichier de donnees : rien a sauvegarder.
        expect_error(service.create_backup, "Aucun fichier")

        service.add_book("Livre", "Auteur", "ISBN-1")
        service.add_user("Alice", "USR-1")

        books_path = Path(tmp) / "books.txt"
        users_path = Path(tmp) / "users.txt"
        original_books = books_path.read_text(encoding="utf-8")
        original_users = users_path.read_text(encoding="utf-8")

        names = service.create_backup()
        assert set(names) == {"books.txt.backup", "users.txt.backup"}
        assert Path(str(books_path) + ".backup").exists()
        assert Path(str(users_path) + ".backup").exists()
        assert (
            Path(str(books_path) + ".backup").read_text(encoding="utf-8")
            == original_books
        )
        assert (
            Path(str(users_path) + ".backup").read_text(encoding="utf-8")
            == original_users
        )

        # Un second backup est refuse avec un message explicite.
        expect_error(service.create_backup, "existe déjà")

        # La sauvegarde ne modifie pas les fichiers courants.
        assert books_path.read_text(encoding="utf-8") == original_books
        assert users_path.read_text(encoding="utf-8") == original_users


def test_repo_data_untouched() -> None:
    assert snapshot_repo_data() == REPO_DATA_BEFORE


TESTS = [
    test_add_book_and_persistence,
    test_add_book_validation,
    test_add_user_and_persistence,
    test_remove_book_rules,
    test_checkout_and_return,
    test_backup,
    test_repo_data_untouched,
]


def main() -> int:
    failures: list[str] = []

    for test in TESTS:
        try:
            test()
        except Exception:
            failures.append(test.__name__)
            print(f"ECHEC  - {test.__name__}")
            traceback.print_exc()
        else:
            print(f"OK     - {test.__name__}")

    print()
    if failures:
        print(f"{len(failures)} test(s) en echec sur {len(TESTS)}.")
        return 1

    print(f"{len(TESTS)} tests reussis.")
    return 0


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
