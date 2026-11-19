"""Modèle de la bibliothèque, indépendant de Tkinter."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from app.models.book import Book
from app.models.user import User

_FORBIDDEN_CHARACTERS = ("|", "\n", "\r")


class LibraryError(Exception):
    """Erreur métier présentée directement à l'utilisateur."""


@dataclass(frozen=True)
class LibraryStats:
    """Compteurs affichés dans l'interface."""

    total: int
    available: int
    borrowed: int
    users: int


def normalize(text: str) -> str:
    """Passe le texte en minuscules et supprime les accents."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


class Library:
    """Collection de livres et d'utilisateurs avec les règles métier."""

    def __init__(
        self,
        books: list[Book] | None = None,
        users: list[User] | None = None,
    ) -> None:
        self.books = list(books or [])
        self.users = list(users or [])

    def find_book(self, isbn: str) -> Book | None:
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def find_user(self, user_id: str) -> User | None:
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def borrower_name(self, book: Book) -> str | None:
        """Renvoie le nom de l'emprunteur, ou None s'il est inconnu."""
        if not book.borrower_id:
            return None
        user = self.find_user(book.borrower_id)
        return user.name if user else None

    def filtered_books(self, query: str = "") -> list[Book]:
        """Filtre les livres par titre, auteur ou ISBN, sans tenir compte des accents."""
        query = query.strip()
        if not query:
            return list(self.books)

        needle = normalize(query)
        return [
            book
            for book in self.books
            if needle in normalize(book.title)
            or needle in normalize(book.author)
            or needle in normalize(book.isbn)
        ]

    def statistics(self) -> LibraryStats:
        borrowed = sum(1 for book in self.books if not book.available)
        return LibraryStats(
            total=len(self.books),
            available=len(self.books) - borrowed,
            borrowed=borrowed,
            users=len(self.users),
        )

    def add_book(self, title: str, author: str, isbn: str) -> Book:
        """Ajoute un livre après validation des champs."""
        title = self._clean_field(title, "Le titre")
        author = self._clean_field(author, "L'auteur")
        isbn = self._clean_field(isbn, "L'ISBN")

        if self.find_book(isbn) is not None:
            raise LibraryError(f"Un livre avec l'ISBN {isbn} existe déjà.")

        book = Book(title=title, author=author, isbn=isbn)
        self.books.append(book)
        return book

    def remove_book(self, isbn: str) -> Book:
        """Supprime un livre et le retire des emprunts des utilisateurs."""
        book = self.find_book(isbn)
        if book is None:
            raise LibraryError("Livre introuvable.")

        self.books.remove(book)
        for user in self.users:
            self._detach_isbn(user, isbn)
        return book

    def borrow(self, isbn: str, user_id: str) -> Book:
        """Attribue un livre disponible à un utilisateur."""
        book = self.find_book(isbn)
        if book is None:
            raise LibraryError("Livre introuvable.")
        if not book.available:
            raise LibraryError("Ce livre est déjà emprunté.")

        user = self.find_user(user_id)
        if user is None:
            raise LibraryError("Utilisateur introuvable.")

        book.available = False
        book.borrower_id = user.user_id
        if isbn not in user.borrowed_isbns:
            user.borrowed_isbns.append(isbn)
        return book

    def return_book(self, isbn: str) -> Book:
        """Rend un livre emprunté disponible."""
        book = self.find_book(isbn)
        if book is None:
            raise LibraryError("Livre introuvable.")
        if book.available:
            raise LibraryError("Ce livre est déjà disponible.")

        for user in self.users:
            self._detach_isbn(user, isbn)
        book.available = True
        book.borrower_id = ""
        return book

    @staticmethod
    def _clean_field(value: str, label: str) -> str:
        value = value.strip()
        if not value:
            raise LibraryError(f"{label} est obligatoire.")
        if any(char in value for char in _FORBIDDEN_CHARACTERS):
            raise LibraryError(
                "Les champs ne peuvent pas contenir « | » ni de retour à la ligne."
            )
        return value

    @staticmethod
    def _detach_isbn(user: User, isbn: str) -> None:
        if isbn in user.borrowed_isbns:
            user.borrowed_isbns.remove(isbn)
