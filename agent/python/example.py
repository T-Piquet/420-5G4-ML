"""Test de fumee du module C++ bibliotheque_py."""

import shutil
import tempfile
from pathlib import Path

import bibliotheque_py as bp

DATA = Path(__file__).resolve().parents[1] / "data"


def main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        books_file = Path(tmp_dir) / "books.txt"
        users_file = Path(tmp_dir) / "users.txt"
        shutil.copy(DATA / "books.txt", books_file)
        shutil.copy(DATA / "users.txt", users_file)

        library = bp.Library()
        files = bp.FileManager(str(books_file), str(users_file))
        files.load_library_data(library)

        print(f"Livres charges : {library.get_total_books()}")
        print(f"Utilisateurs : {len(library.get_all_users())}")

        isbn = "9780000000001"
        library.add_book(bp.Book("Un nouveau livre", "Un auteur", isbn))
        book = library.find_book_by_isbn(isbn)
        print(f"Livre ajoute : {book.title}")

        user = library.find_user_by_id("USR001") or library.get_all_users()[0]
        print(f"Emprunt : {library.check_out_book(isbn, user.user_id)}")
        print(f"Livre disponible : {book.available}")
        print(f"Retour : {library.return_book(isbn)}")

        files.save_library_data(library)
        print(f"Sauvegarde ecrite dans {tmp_dir}")


if __name__ == "__main__":
    main()
