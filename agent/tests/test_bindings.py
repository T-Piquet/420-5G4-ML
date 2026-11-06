#!/usr/bin/env python3
"""Tests d'interface et de persistance pour le module bibliotheque_cpp.

Execution depuis le repertoire agent/ :
    PYTHONPATH=build python3 tests/test_bindings.py

ou simplement :
    python3 tests/test_bindings.py

Le script ajoute automatiquement agent/build a sys.path. Il ne modifie jamais
agent/data : tous les tests d'ecriture utilisent un repertoire temporaire.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import traceback
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = AGENT_DIR / "build"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

try:
    import bibliotheque_cpp as b
except ImportError:
    print("ERREUR : impossible d'importer bibliotheque_cpp.")
    print("Compilez d'abord le module :")
    print(f"  cmake -S {AGENT_DIR} -B {BUILD_DIR}")
    print(f"  cmake --build {BUILD_DIR}")
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


def test_book() -> None:
    book = b.Book()
    assert book.getTitle() == ""
    assert book.getAuthor() == ""
    assert book.getISBN() == ""
    assert book.getAvailability() is True
    assert book.getBorrowerId() == ""

    book = b.Book("Le Petit Prince", "Antoine de Saint-Exupery", "ISBN-1")
    assert book.getTitle() == "Le Petit Prince"
    assert book.getAuthor() == "Antoine de Saint-Exupery"
    assert book.getISBN() == "ISBN-1"
    assert book.getAvailability() is True
    assert book.getBorrowerId() == ""

    book.setTitle("Titre modifie")
    book.setAuthor("Auteur modifie")
    book.setISBN("ISBN-2")
    book.setAvailability(False)
    book.setBorrowerId("USR-1")
    assert book.getTitle() == "Titre modifie"
    assert book.getAuthor() == "Auteur modifie"
    assert book.getISBN() == "ISBN-2"
    assert book.getAvailability() is False
    assert book.getBorrowerId() == "USR-1"

    book.setAvailability(True)
    book.setBorrowerId("")
    book.checkOut("USR-1")
    assert book.getAvailability() is False
    assert book.getBorrowerId() == "USR-1"
    assert book.toFileFormat() == "Titre modifie|Auteur modifie|ISBN-2|0|USR-1"

    # Un second checkOut ne doit pas changer l'emprunteur.
    book.checkOut("USR-2")
    assert book.getBorrowerId() == "USR-1"

    book.returnBook()
    assert book.getAvailability() is True
    assert book.getBorrowerId() == ""
    assert book.toFileFormat() == "Titre modifie|Auteur modifie|ISBN-2|1|"

    parsed = b.Book()
    parsed.fromFileFormat("Les Miserables|Victor Hugo|ISBN-3|0|USR-2")
    assert parsed.getTitle() == "Les Miserables"
    assert parsed.getAuthor() == "Victor Hugo"
    assert parsed.getISBN() == "ISBN-3"
    assert parsed.getAvailability() is False
    assert parsed.getBorrowerId() == "USR-2"


def test_user() -> None:
    user = b.User()
    assert user.getName() == ""
    assert user.getUserId() == ""
    assert user.getBorrowedBooks() == []

    user = b.User("Alice", "USR-1")
    assert user.getName() == "Alice"
    assert user.getUserId() == "USR-1"
    assert user.getBorrowedBooks() == []

    user.setName("Alice Martin")
    user.setUserId("USR-2")
    assert user.getName() == "Alice Martin"
    assert user.getUserId() == "USR-2"

    user.borrowBook("ISBN-1")
    user.borrowBook("ISBN-1")  # doublon ignore
    user.borrowBook("ISBN-2")
    assert user.getBorrowedBooks() == ["ISBN-1", "ISBN-2"]
    assert user.hasBorrowedBook("ISBN-1") is True
    assert user.hasBorrowedBook("ISBN-3") is False
    assert user.getNumberOfBorrowedBooks() == 2
    assert user.toFileFormat() == "Alice Martin|USR-2|ISBN-1,ISBN-2"

    user.returnBook("ISBN-1")
    assert user.getBorrowedBooks() == ["ISBN-2"]
    assert user.hasBorrowedBook("ISBN-1") is False
    user.returnBook("ISBN-1")  # retour d'un livre absent : pas d'erreur
    assert user.getNumberOfBorrowedBooks() == 1

    parsed = b.User()
    parsed.fromFileFormat("Bob|USR-3|ISBN-4,ISBN-5")
    assert parsed.getName() == "Bob"
    assert parsed.getUserId() == "USR-3"
    assert parsed.getBorrowedBooks() == ["ISBN-4", "ISBN-5"]

    empty = b.User("Charlie", "USR-4")
    assert empty.toFileFormat() == "Charlie|USR-4|"
    parsed_empty = b.User()
    parsed_empty.fromFileFormat("Charlie|USR-4|")
    assert parsed_empty.getBorrowedBooks() == []


def test_library_books() -> None:
    library = b.Library()
    assert library.getTotalBooks() == 0
    assert library.getAvailableBookCount() == 0
    assert library.getCheckedOutBookCount() == 0

    book1 = b.Book("Le Petit Prince", "Antoine de Saint-Exupery", "ISBN-1")
    book2 = b.Book("Les Miserables", "Victor Hugo", "ISBN-2")
    book3 = b.Book("Notre-Dame de Paris", "Victor Hugo", "ISBN-3")
    for book in (book1, book2, book3):
        library.addBook(book)

    assert library.getTotalBooks() == 3
    assert library.getAvailableBookCount() == 3
    assert library.getCheckedOutBookCount() == 0

    assert library.findBookByISBN("ISBN-1").getTitle() == "Le Petit Prince"
    assert library.findBookByISBN("ISBN-2").getAuthor() == "Victor Hugo"
    assert library.findBookByISBN("ISBN-999") is None

    assert len(library.searchBooksByTitle("petit")) == 1
    assert len(library.searchBooksByTitle("PETIT")) == 1
    assert len(library.searchBooksByTitle("miser")) == 1
    assert len(library.searchBooksByTitle("absent")) == 0
    assert len(library.searchBooksByAuthor("hugo")) == 2
    assert len(library.searchBooksByAuthor("HUGO")) == 2
    assert len(library.searchBooksByAuthor("saint")) == 1

    all_books = library.getAllBooks()
    assert len(all_books) == 3
    assert {book.getISBN() for book in all_books} == {"ISBN-1", "ISBN-2", "ISBN-3"}

    # Les collections renvoient des copies : modifier une copie ne modifie
    # pas la bibliotheque.
    all_books[0].setTitle("Titre copie")
    assert library.findBookByISBN("ISBN-1").getTitle() == "Le Petit Prince"

    # findBookByISBN renvoie une reference interne : la modification est visible.
    library.findBookByISBN("ISBN-1").setTitle("Titre reference")
    assert library.findBookByISBN("ISBN-1").getTitle() == "Titre reference"

    assert library.removeBook("ISBN-2") is True
    assert library.findBookByISBN("ISBN-2") is None
    assert library.getTotalBooks() == 2
    assert library.removeBook("ISBN-2") is False


def test_library_users() -> None:
    library = b.Library()
    user1 = b.User("Alice", "USR-1")
    user2 = b.User("Bob", "USR-2")
    library.addUser(user1)
    library.addUser(user2)

    assert len(library.getAllUsers()) == 2
    assert library.findUserById("USR-1").getName() == "Alice"
    assert library.findUserById("USR-2").getName() == "Bob"
    assert library.findUserById("USR-999") is None

    # getAllUsers renvoie des copies.
    users = library.getAllUsers()
    users[0].setName("Nom copie")
    assert library.findUserById("USR-1").getName() == "Alice"

    # findUserById renvoie une reference interne.
    library.findUserById("USR-2").setName("Bob Martin")
    assert library.findUserById("USR-2").getName() == "Bob Martin"


def test_library_loans() -> None:
    library = b.Library()
    library.addBook(b.Book("Livre 1", "Auteur 1", "ISBN-1"))
    library.addBook(b.Book("Livre 2", "Auteur 2", "ISBN-2"))
    library.addUser(b.User("Alice", "USR-1"))
    library.addUser(b.User("Bob", "USR-2"))

    assert library.checkOutBook("ISBN-1", "USR-1") is True
    assert library.findBookByISBN("ISBN-1").getAvailability() is False
    assert library.findBookByISBN("ISBN-1").getBorrowerId() == "USR-1"
    assert library.findUserById("USR-1").hasBorrowedBook("ISBN-1") is True
    assert library.getAvailableBookCount() == 1
    assert library.getCheckedOutBookCount() == 1

    # Livre deja emprunte.
    assert library.checkOutBook("ISBN-1", "USR-2") is False
    assert library.findBookByISBN("ISBN-1").getBorrowerId() == "USR-1"
    assert library.findUserById("USR-2").getBorrowedBooks() == []

    # Livre inexistant.
    assert library.checkOutBook("ISBN-999", "USR-1") is False

    # Utilisateur inexistant.
    assert library.checkOutBook("ISBN-2", "USR-999") is False
    assert library.findBookByISBN("ISBN-2").getAvailability() is True

    assert library.returnBook("ISBN-1") is True
    assert library.findBookByISBN("ISBN-1").getAvailability() is True
    assert library.findBookByISBN("ISBN-1").getBorrowerId() == ""
    assert library.findUserById("USR-1").hasBorrowedBook("ISBN-1") is False
    assert library.getAvailableBookCount() == 2
    assert library.getCheckedOutBookCount() == 0

    # Retour d'un livre deja disponible.
    assert library.returnBook("ISBN-1") is False

    # Retour d'un livre inexistant.
    assert library.returnBook("ISBN-999") is False


def test_persistence_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        books_path = tmp_dir / "books.txt"
        users_path = tmp_dir / "users.txt"

        library = b.Library()
        books = [
            b.Book("Le Petit Prince", "Antoine de Saint-Exupery", "ISBN-1"),
            b.Book("Les Miserables", "Victor Hugo", "ISBN-2"),
            b.Book("Notre-Dame de Paris", "Victor Hugo", "ISBN-3"),
        ]
        users = [
            b.User("Alice", "USR-1"),
            b.User("Bob", "USR-2"),
        ]
        for book in books:
            library.addBook(book)
        for user in users:
            library.addUser(user)

        assert library.checkOutBook("ISBN-1", "USR-1") is True
        assert library.checkOutBook("ISBN-2", "USR-2") is True

        file_manager = b.FileManager(str(books_path), str(users_path))
        assert file_manager.saveLibraryData(library) is True
        assert books_path.exists() is True
        assert users_path.exists() is True
        assert books_path.read_text(encoding="utf-8").strip() != ""
        assert users_path.read_text(encoding="utf-8").strip() != ""

        # Rechargement dans une instance vierge.
        reloaded = b.Library()
        reload_manager = b.FileManager(str(books_path), str(users_path))
        assert reload_manager.loadLibraryData(reloaded) is True

        assert reloaded.getTotalBooks() == 3
        assert len(reloaded.getAllUsers()) == 2
        assert reloaded.getAvailableBookCount() == 1
        assert reloaded.getCheckedOutBookCount() == 2

        expected_books = {
            "ISBN-1": ("Le Petit Prince", "Antoine de Saint-Exupery", False, "USR-1"),
            "ISBN-2": ("Les Miserables", "Victor Hugo", False, "USR-2"),
            "ISBN-3": ("Notre-Dame de Paris", "Victor Hugo", True, ""),
        }
        for isbn, (title, author, available, borrower) in expected_books.items():
            loaded = reloaded.findBookByISBN(isbn)
            assert loaded is not None
            assert loaded.getTitle() == title
            assert loaded.getAuthor() == author
            assert loaded.getAvailability() is available
            assert loaded.getBorrowerId() == borrower

        expected_users = {
            "USR-1": ("Alice", ["ISBN-1"]),
            "USR-2": ("Bob", ["ISBN-2"]),
        }
        for user_id, (name, borrowed) in expected_users.items():
            loaded_user = reloaded.findUserById(user_id)
            assert loaded_user is not None
            assert loaded_user.getName() == name
            assert sorted(loaded_user.getBorrowedBooks()) == sorted(borrowed)

        # Les lignes sauvegardees correspondent bien aux objets recharges.
        saved_book_lines = set(books_path.read_text(encoding="utf-8").splitlines())
        for book in reloaded.getAllBooks():
            assert book.toFileFormat() in saved_book_lines

        saved_user_lines = set(users_path.read_text(encoding="utf-8").splitlines())
        for user in reloaded.getAllUsers():
            assert user.toFileFormat() in saved_user_lines


def test_backup() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        books_path = tmp_dir / "books.txt"
        users_path = tmp_dir / "users.txt"

        library = b.Library()
        library.addBook(b.Book("Livre", "Auteur", "ISBN-1"))
        library.addUser(b.User("Alice", "USR-1"))

        file_manager = b.FileManager(str(books_path), str(users_path))
        assert file_manager.saveLibraryData(library) is True

        original_books = books_path.read_text(encoding="utf-8")
        original_users = users_path.read_text(encoding="utf-8")

        file_manager.createBackup()

        books_backup = Path(str(books_path) + ".backup")
        users_backup = Path(str(users_path) + ".backup")
        assert books_backup.exists() is True
        assert users_backup.exists() is True
        assert books_backup.read_text(encoding="utf-8") == original_books
        assert users_backup.read_text(encoding="utf-8") == original_users

        # Un second backup doit echouer : la destination existe deja.
        try:
            file_manager.createBackup()
        except (RuntimeError, OSError):
            pass
        else:
            raise AssertionError("createBackup() aurait dû lever une exception")


def test_repo_data_untouched() -> None:
    assert snapshot_repo_data() == REPO_DATA_BEFORE


TESTS = [
    test_book,
    test_user,
    test_library_books,
    test_library_users,
    test_library_loans,
    test_persistence_roundtrip,
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
    if main() == 0:
        sys.exit(0)
    sys.exit(1)
