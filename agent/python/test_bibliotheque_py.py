"""Test minimal du module pybind11 sur une copie de data/."""

import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BUILD_DIR = Path(os.environ.get("BIBLIOTHEQUE_PY_BUILD", ROOT / "build"))

sys.path.insert(0, str(BUILD_DIR))

import bibliotheque_py  # noqa: E402


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_hashes = {
        name: file_hash(DATA_DIR / name) for name in ("books.txt", "users.txt")
    }

    with tempfile.TemporaryDirectory() as tmp:
        copied_data = Path(tmp) / "data"
        shutil.copytree(DATA_DIR, copied_data)

        library = bibliotheque_py.load_library(str(copied_data))
        books = library.all_books()

        expected_count = sum(
            1
            for line in (copied_data / "books.txt").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

        assert len(books) == expected_count
        assert library.total_books == expected_count
        assert all(isinstance(book, bibliotheque_py.Book) for book in books)

        by_title = {book.title: book for book in books}
        assert by_title["Le Petit Prince"].available is True
        assert by_title["Les Misérables"].available is False
        assert by_title["Les Misérables"].borrower_id == "USR001"
        assert by_title["Le Petit Prince"].author == "Antoine de Saint-Exupéry"

        assert library.available_count == sum(1 for book in books if book.available)
        assert library.checked_out_count == library.total_books - library.available_count
        assert library.users_count > 0

        par_titre = library.search_books_by_title("petit prince")
        assert [book.title for book in par_titre] == ["Le Petit Prince"]

        par_auteur = library.search_books_by_author("victor hugo")
        assert len(par_auteur) == 5
        assert all(book.author == "Victor Hugo" for book in par_auteur)

        assert len(library.search_books_by_title("")) == len(books)
        assert len(library.search_books_by_author("")) == len(books)

        livre = library.find_book_by_isbn("9782070612758")
        assert livre is not None
        assert livre.title == "Le Petit Prince"
        assert library.find_book_by_isbn("0000000000000") is None

        disponibles = library.available_books()
        assert len(disponibles) == library.available_count
        assert all(book.available for book in disponibles)
        assert {book.isbn for book in disponibles} == {
            book.isbn for book in books if book.available
        }
        assert all(isinstance(book, bibliotheque_py.Book) for book in disponibles)

        utilisateurs = library.all_users()
        assert len(utilisateurs) == library.users_count
        assert all(isinstance(user, bibliotheque_py.User) for user in utilisateurs)
        assert {user.user_id for user in utilisateurs} >= {
            "USR001",
            "USR002",
            "USR015",
            "USR016",
        }

        avant = library.available_count
        assert library.check_out_book("9782070612758", "USR015") is True
        assert library.available_count == avant - 1
        emprunte = library.find_book_by_isbn("9782070612758")
        assert emprunte.available is False
        assert emprunte.borrower_id == "USR015"
        assert "9782070612758" in next(
            user for user in library.all_users() if user.user_id == "USR015"
        ).borrowed_books

        avant = library.available_count
        assert library.check_out_book("9782253096337", "USR016") is False
        assert library.available_count == avant
        deja_emprunte = library.find_book_by_isbn("9782253096337")
        assert deja_emprunte.available is False
        assert deja_emprunte.borrower_id == "USR001"
        assert "9782253096337" not in next(
            user for user in library.all_users() if user.user_id == "USR016"
        ).borrowed_books

        avant = library.available_count
        assert library.return_book("9782070413119") is True
        assert library.available_count == avant + 1
        retourne = library.find_book_by_isbn("9782070413119")
        assert retourne.available is True
        assert retourne.borrower_id == ""
        assert "9782070413119" not in next(
            user for user in library.all_users() if user.user_id == "USR002"
        ).borrowed_books

        avant = library.users_count
        assert library.add_user("Nouvel Utilisateur", "USR099") is True
        assert library.users_count == avant + 1
        nouveau = next(
            user for user in library.all_users() if user.user_id == "USR099"
        )
        assert nouveau.name == "Nouvel Utilisateur"
        assert nouveau.borrowed_books == []

        avant = library.users_count
        assert library.add_user("Doublon", "USR001") is False
        assert library.users_count == avant
        assert next(
            user for user in library.all_users() if user.user_id == "USR001"
        ).name == "Marie Dubois"

        avant_total = library.total_books
        avant_dispo = library.available_count
        assert library.add_book("Livre Test", "Auteur Test", "9780000000001") is True
        assert library.total_books == avant_total + 1
        assert library.available_count == avant_dispo + 1
        ajoute = library.find_book_by_isbn("9780000000001")
        assert ajoute.available is True
        assert ajoute.borrower_id == ""

        avant_total = library.total_books
        assert library.add_book("Doublon", "Auteur", "9780000000001") is False
        assert library.total_books == avant_total

        assert library.remove_book("9780000000001") is True
        assert library.total_books == avant_total - 1
        assert library.available_count == avant_dispo
        assert library.find_book_by_isbn("9780000000001") is None

        assert library.add_user("Utilisateur Sauvegarde", "USR098") is True
        assert library.add_book(
            "Livre Sauvegarde", "Auteur Sauvegarde", "9780000000003"
        ) is True
        assert bibliotheque_py.save_library(library, str(copied_data)) is True

        books_text = (copied_data / "books.txt").read_text(encoding="utf-8")
        users_text = (copied_data / "users.txt").read_text(encoding="utf-8")
        assert "Livre Sauvegarde|Auteur Sauvegarde|9780000000003|1|" in books_text
        assert "Utilisateur Sauvegarde|USR098|" in users_text

        rechargee = bibliotheque_py.load_library(str(copied_data))
        assert (
            rechargee.find_book_by_isbn("9780000000003").title == "Livre Sauvegarde"
        )
        assert any(
            user.user_id == "USR098" and user.name == "Utilisateur Sauvegarde"
            for user in rechargee.all_users()
        )

        assert bibliotheque_py.create_backup(str(copied_data)) is True
        books_backup = copied_data / "books.txt.backup"
        users_backup = copied_data / "users.txt.backup"
        assert books_backup.exists()
        assert users_backup.exists()
        assert books_backup.read_bytes() == (copied_data / "books.txt").read_bytes()
        assert users_backup.read_bytes() == (copied_data / "users.txt").read_bytes()

        backups_hashes = {
            "books.txt.backup": file_hash(books_backup),
            "users.txt.backup": file_hash(users_backup),
        }
        assert bibliotheque_py.create_backup(str(copied_data)) is False
        assert backups_hashes == {
            "books.txt.backup": file_hash(books_backup),
            "users.txt.backup": file_hash(users_backup),
        }

    assert source_hashes == {
        name: file_hash(DATA_DIR / name) for name in ("books.txt", "users.txt")
    }

    print(f"OK : {len(books)} livres chargés depuis une copie de data/")


if __name__ == "__main__":
    main()
