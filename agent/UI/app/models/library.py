"""Modèle de la bibliothèque : façade Python sur le cœur C++.

L'état des livres et des utilisateurs vit dans le module natif
``bibliotheque_core``. Cette classe conserve l'API utilisée par le contrôleur
et convertit les objets C++ en dataclasses prêtes à afficher.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any

try:
    from app import bibliotheque_core as _native
except ImportError as error:  # pragma: no cover - dépend du build natif
    _native = None
    _NATIVE_IMPORT_ERROR: ImportError | None = error
else:
    _NATIVE_IMPORT_ERROR = None

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


def require_native() -> Any:
    """Renvoie le module C++ ou explique comment le compiler."""
    if _native is None:
        raise RuntimeError(
            "Le module natif « bibliotheque_core » n'a pas pu être importé.\n"
            "Compilez-le depuis agent/ avec : ./bindings/build.sh"
        ) from _NATIVE_IMPORT_ERROR
    return _native


def normalize(text: str) -> str:
    """Passe le texte en minuscules et supprime les accents."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


class Library:
    """Collection de livres et d'utilisateurs adossée au C++."""

    def __init__(
        self,
        books: list[Book] | None = None,
        users: list[User] | None = None,
    ) -> None:
        self._native = require_native()
        self._core = self._native.Library()

        for book in books or []:
            self._core.add_book(self._to_native_book(book))
        for user in users or []:
            self._core.add_user(self._to_native_user(user))

    @property
    def native(self) -> Any:
        """Objet C++ sous-jacent, réservé au dépôt de données."""
        return self._core

    @property
    def books(self) -> list[Book]:
        """Photographie des livres, dans l'ordre du fichier."""
        return [self._to_book(book) for book in self._core.all_books()]

    @property
    def users(self) -> list[User]:
        """Photographie des utilisateurs."""
        return [self._to_user(user) for user in self._core.all_users()]

    def find_book(self, isbn: str) -> Book | None:
        book = self._core.find_book(isbn)
        return None if book is None else self._to_book(book)

    def find_user(self, user_id: str) -> User | None:
        user = self._core.find_user(user_id)
        return None if user is None else self._to_user(user)

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
            return self.books

        needle = normalize(query)
        return [
            book
            for book in self.books
            if needle in normalize(book.title)
            or needle in normalize(book.author)
            or needle in normalize(book.isbn)
        ]

    def filtered_users(self, query: str = "") -> list[User]:
        """Filtre les utilisateurs par nom ou identifiant, sans tenir compte des accents."""
        query = query.strip()
        if not query:
            return self.users

        needle = normalize(query)
        return [
            user
            for user in self.users
            if needle in normalize(user.name)
            or needle in normalize(user.user_id)
        ]

    def statistics(self) -> LibraryStats:
        return LibraryStats(
            total=self._core.total_books(),
            available=self._core.available_count(),
            borrowed=self._core.checked_out_count(),
            users=len(self._core.all_users()),
        )

    def add_book(self, title: str, author: str, isbn: str) -> Book:
        """Ajoute un livre après validation des champs."""
        title = self._clean_field(title, "Le titre")
        author = self._clean_field(author, "L'auteur")
        isbn = self._clean_field(isbn, "L'ISBN")

        if self._core.find_book(isbn) is not None:
            raise LibraryError(f"Un livre avec l'ISBN {isbn} existe déjà.")

        book = self._native.Book(title, author, isbn)
        self._core.add_book(book)
        return self._to_book(book)

    def add_user(self, name: str, user_id: str) -> User:
        """Ajoute un utilisateur après validation des champs."""
        name = self._clean_field(name, "Le nom")
        user_id = self._clean_field(user_id, "L'identifiant")

        if self._core.find_user(user_id) is not None:
            raise LibraryError(
                f"Un utilisateur avec l'identifiant {user_id} existe déjà."
            )

        user = self._native.User(name, user_id)
        self._core.add_user(user)
        return self._to_user(user)

    def remove_book(self, isbn: str) -> Book:
        """Supprime un livre et le retire des emprunts des utilisateurs."""
        book = self.find_book(isbn)
        if book is None or not self._core.remove_book(isbn):
            raise LibraryError("Livre introuvable.")
        return book

    def borrow(self, isbn: str, user_id: str) -> Book:
        """Attribue un livre disponible à un utilisateur."""
        book = self._core.find_book(isbn)
        if book is None:
            raise LibraryError("Livre introuvable.")
        if not book.available:
            raise LibraryError("Ce livre est déjà emprunté.")
        if self._core.find_user(user_id) is None:
            raise LibraryError("Utilisateur introuvable.")
        if not self._core.check_out_book(isbn, user_id):
            raise LibraryError("Impossible d'emprunter ce livre.")

        borrowed = self.find_book(isbn)
        if borrowed is None:  # pragma: no cover - incohérence interne
            raise LibraryError("Livre introuvable.")
        return borrowed

    def return_book(self, isbn: str) -> Book:
        """Rend un livre emprunté disponible."""
        book = self._core.find_book(isbn)
        if book is None:
            raise LibraryError("Livre introuvable.")
        if book.available:
            raise LibraryError("Ce livre est déjà disponible.")
        if not self._core.return_book(isbn):
            raise LibraryError("Impossible de retourner ce livre.")

        returned = self.find_book(isbn)
        if returned is None:  # pragma: no cover - incohérence interne
            raise LibraryError("Livre introuvable.")
        return returned

    def _to_native_book(self, book: Book) -> Any:
        native_book = self._native.Book(book.title, book.author, book.isbn)
        native_book.available = book.available
        native_book.borrower_id = book.borrower_id
        return native_book

    def _to_native_user(self, user: User) -> Any:
        native_user = self._native.User(user.name, user.user_id)
        for isbn in user.borrowed_isbns:
            native_user.borrow_book(isbn)
        return native_user

    @staticmethod
    def _to_book(book: Any) -> Book:
        return Book(
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            available=book.available,
            borrower_id=book.borrower_id,
        )

    @staticmethod
    def _to_user(user: Any) -> User:
        return User(
            name=user.name,
            user_id=user.user_id,
            borrowed_isbns=list(user.borrowed_isbns),
        )

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
