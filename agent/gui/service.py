"""Couche de service entre l'interface CustomTkinter et le module C++.

Les vues ne manipulent jamais directement les objets pybind11 : elles recoivent
des snapshots Python (dataclasses) pour eviter les problemes de duree de vie
des pointeurs C++.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = AGENT_DIR / "build"
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

try:
    import bibliotheque_cpp as _cpp
except ImportError:
    _cpp = None


@dataclass(frozen=True)
class BookView:
    title: str
    author: str
    isbn: str
    available: bool
    borrower_id: str


@dataclass(frozen=True)
class UserView:
    name: str
    user_id: str
    borrowed_books: tuple[str, ...]
    borrowed_titles: tuple[str, ...]


@dataclass(frozen=True)
class LibraryStats:
    total_books: int
    available_books: int
    checked_out_books: int
    users: int


@dataclass(frozen=True)
class LoanView:
    book_title: str
    author: str
    isbn: str
    borrower_id: str
    borrower_name: str


class LibraryService:
    """Charge la bibliotheque et fournit des lectures pretes pour l'UI."""

    def __init__(self, data_dir: str | Path) -> None:
        if _cpp is None:
            raise RuntimeError(
                "Le module bibliotheque_cpp est introuvable. "
                "Compilez-le avec CMake avant de lancer l'interface."
            )

        self.data_dir = Path(data_dir).expanduser().resolve()
        self.books_path = self.data_dir / "books.txt"
        self.users_path = self.data_dir / "users.txt"
        self.library = _cpp.Library()
        self.file_manager = _cpp.FileManager(
            str(self.books_path), str(self.users_path)
        )
        self.load_error: str | None = None
        self.reload()

    def reload(self) -> None:
        """Recharge les fichiers dans une Library neuve (loadLibraryData ajoute)."""
        if _cpp is None:
            return

        self.library = _cpp.Library()
        self.file_manager = _cpp.FileManager(
            str(self.books_path), str(self.users_path)
        )

        missing = [
            path.name
            for path in (self.books_path, self.users_path)
            if not path.exists()
        ]

        try:
            loaded = self.file_manager.loadLibraryData(self.library)
        except Exception as exc:  # erreur de fichier ou de format
            self.load_error = f"Impossible de charger les données : {exc}"
            return

        if missing:
            self.load_error = (
                "Fichier(s) de données manquant(s) : " + ", ".join(missing)
            )
        elif not loaded:
            self.load_error = "Aucune donnée n'a pu être chargée."
        else:
            self.load_error = None

    def get_books(self) -> list[BookView]:
        if self.library is None:
            return []
        return [
            BookView(
                title=book.getTitle(),
                author=book.getAuthor(),
                isbn=book.getISBN(),
                available=book.getAvailability(),
                borrower_id=book.getBorrowerId(),
            )
            for book in self.library.getAllBooks()
        ]

    def get_users(self) -> list[UserView]:
        if self.library is None:
            return []

        titles_by_isbn = {book.isbn: book.title for book in self.get_books()}
        users: list[UserView] = []
        for user in self.library.getAllUsers():
            borrowed = tuple(user.getBorrowedBooks())
            users.append(
                UserView(
                    name=user.getName(),
                    user_id=user.getUserId(),
                    borrowed_books=borrowed,
                    borrowed_titles=tuple(
                        titles_by_isbn.get(isbn, isbn) for isbn in borrowed
                    ),
                )
            )
        return users

    def get_stats(self) -> LibraryStats:
        if self.library is None:
            return LibraryStats(0, 0, 0, 0)
        return LibraryStats(
            total_books=self.library.getTotalBooks(),
            available_books=self.library.getAvailableBookCount(),
            checked_out_books=self.library.getCheckedOutBookCount(),
            users=len(self.library.getAllUsers()),
        )

    def search_books(self, query: str) -> list[BookView]:
        """Recherche insensible a la casse sur le titre et l'auteur.

        Le filtrage est fait en Python pour gerer correctement les accents,
        contrairement au ::tolower octet par octet du code C++.
        """
        normalized = query.strip().casefold()
        books = self.get_books()
        if not normalized:
            return books
        return [
            book
            for book in books
            if normalized in book.title.casefold()
            or normalized in book.author.casefold()
        ]

    def get_loans(self) -> list[LoanView]:
        users_by_id = {user.user_id: user for user in self.get_users()}
        loans: list[LoanView] = []
        for book in self.get_books():
            if book.available:
                continue
            borrower = users_by_id.get(book.borrower_id)
            loans.append(
                LoanView(
                    book_title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    borrower_id=book.borrower_id,
                    borrower_name=borrower.name if borrower else "Inconnu",
                )
            )
        return loans
