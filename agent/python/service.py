"""Service Python encapsulant le coeur C++ de la bibliotheque.

Le service expose uniquement des donnees Python simples (dict, listes, chaines)
afin que les widgets de l'interface graphique ne conservent jamais de pointeurs
Book* ou User* vers des objets C++.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from bibliotheque_py import Book, FileManager, Library, User

BOOKS_FILENAME = "books.txt"
USERS_FILENAME = "users.txt"

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_FIXTURES_DIR = BASE_DIR.parent / "apprentissage" / "datas"


def book_to_dict(book: Book) -> dict:
    """Convertit un Book C++ en dictionnaire Python autonome."""
    return {
        "title": book.getTitle(),
        "author": book.getAuthor(),
        "isbn": book.getISBN(),
        "available": book.getAvailability(),
        "borrower_id": book.getBorrowerId(),
    }


def user_to_dict(user: User) -> dict:
    """Convertit un User C++ en dictionnaire Python autonome."""
    borrowed = list(user.getBorrowedBooks())
    return {
        "name": user.getName(),
        "user_id": user.getUserId(),
        "borrowed_books": borrowed,
        "borrowed_count": len(borrowed),
    }


class LibraryService:
    """Encapsule Library et FileManager avec une API adaptee a la GUI."""

    def __init__(
        self,
        data_dir: str | Path | None = None,
        fixtures_dir: str | Path | None = None,
        seed: bool = True,
    ) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
        self.fixtures_dir = (
            Path(fixtures_dir) if fixtures_dir is not None else DEFAULT_FIXTURES_DIR
        )
        self.books_file = self.data_dir / BOOKS_FILENAME
        self.users_file = self.data_dir / USERS_FILENAME

        self.data_dir.mkdir(parents=True, exist_ok=True)
        if seed:
            self._seed_data()

        self._file_manager = FileManager(str(self.books_file), str(self.users_file))
        self._library = Library()

    def _seed_data(self) -> bool:
        """Copie les fixtures si le dossier de travail est vide."""
        if any(self.data_dir.iterdir()):
            return False

        copied = False
        for filename in (BOOKS_FILENAME, USERS_FILENAME):
            source = self.fixtures_dir / filename
            if source.is_file():
                shutil.copy2(source, self.data_dir / filename)
                copied = True
        return copied

    # Chargement et sauvegarde

    def load(self) -> bool:
        """Charge books.txt et users.txt dans une bibliotheque neuve."""
        self._library = Library()
        return self._file_manager.loadLibraryData(self._library)

    def save(self) -> bool:
        """Ecrit l'etat courant dans books.txt et users.txt."""
        return self._file_manager.saveLibraryData(self._library)

    def create_backup(self) -> None:
        """Cree les fichiers .backup a partir des fichiers courants."""
        self._file_manager.createBackup()

    # Livres

    def get_books(self) -> list[dict]:
        return [book_to_dict(book) for book in self._library.getAllBooks()]

    def get_available_books(self) -> list[dict]:
        return [
            book_to_dict(book) for book in self._library.getAvailableBooks()
        ]

    def find_book(self, isbn: str) -> dict | None:
        book = self._library.findBookByISBN(isbn)
        return book_to_dict(book) if book is not None else None

    def search_books(self, query: str, by: str = "title") -> list[dict]:
        if by == "title":
            results = self._library.searchBooksByTitle(query)
        elif by == "author":
            results = self._library.searchBooksByAuthor(query)
        else:
            raise ValueError("Critere de recherche invalide : 'title' ou 'author'.")
        return [book_to_dict(book) for book in results]

    def add_book(self, title: str, author: str, isbn: str) -> dict:
        isbn = isbn.strip()
        if not isbn:
            raise ValueError("L'ISBN est obligatoire.")
        if self._library.findBookByISBN(isbn) is not None:
            raise ValueError(f"Un livre avec l'ISBN {isbn} existe deja.")

        book = Book(title, author, isbn)
        self._library.addBook(book)
        return self.find_book(isbn)

    def remove_book(self, isbn: str) -> bool:
        return self._library.removeBook(isbn)

    # Utilisateurs

    def get_users(self) -> list[dict]:
        return [user_to_dict(user) for user in self._library.getAllUsers()]

    def find_user(self, user_id: str) -> dict | None:
        user = self._library.findUserById(user_id)
        return user_to_dict(user) if user is not None else None

    def add_user(self, name: str, user_id: str) -> dict:
        user_id = user_id.strip()
        if not user_id:
            raise ValueError("L'ID utilisateur est obligatoire.")
        if self._library.findUserById(user_id) is not None:
            raise ValueError(f"Un utilisateur avec l'ID {user_id} existe deja.")

        user = User(name, user_id)
        self._library.addUser(user)
        return self.find_user(user_id)

    # Emprunts

    def check_out(self, isbn: str, user_id: str) -> bool:
        return self._library.checkOutBook(isbn, user_id)

    def return_book(self, isbn: str) -> bool:
        return self._library.returnBook(isbn)

    # Statistiques

    def get_stats(self) -> dict:
        return {
            "total_books": self._library.getTotalBooks(),
            "available_books": self._library.getAvailableBookCount(),
            "checked_out_books": self._library.getCheckedOutBookCount(),
            "total_users": len(self._library.getAllUsers()),
        }
