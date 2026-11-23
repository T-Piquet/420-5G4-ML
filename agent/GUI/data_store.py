"""Accès aux données de la bibliothèque (compatible avec la CLI C++).

Formats des fichiers, identiques à `agent/filemanager.cpp` :
- books.txt : titre|auteur|isbn|1ou0|idEmprunteur
- users.txt : nom|id|isbn1,isbn2  (le « | » final est présent même sans emprunt)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


class StoreError(Exception):
    """Erreur de validation ou opération impossible sur la bibliothèque."""


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    available: bool = True
    borrower_id: str = ""


@dataclass
class User:
    name: str
    user_id: str
    borrowed: list[str] = field(default_factory=list)


def _validate(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise StoreError(f"{label} obligatoire.")
    if "|" in value:
        raise StoreError(f"{label} ne peut pas contenir le caractère « | ».")
    return value


class LibraryStore:
    """Bibliothèque en mémoire, chargée depuis et sauvegardée vers `data_dir`."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.books_file = self.data_dir / "books.txt"
        self.users_file = self.data_dir / "users.txt"
        self.books: list[Book] = []
        self.users: list[User] = []

    # ------------------------------------------------------------------ I/O
    def load(self) -> "LibraryStore":
        self.books = []
        self.users = []

        if self.books_file.is_file():
            for line in self.books_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) != 5:
                    raise StoreError(f"Ligne de livre invalide : {line!r}")
                title, author, isbn, flag, borrower = parts
                self.books.append(Book(title, author, isbn, flag == "1", borrower))

        if self.users_file.is_file():
            for line in self.users_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) not in (2, 3):
                    raise StoreError(f"Ligne d'utilisateur invalide : {line!r}")
                borrowed = [isbn for isbn in (parts[2] if len(parts) == 3 else "").split(",") if isbn]
                self.users.append(User(parts[0], parts[1], borrowed))

        return self

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        book_lines = [
            f"{book.title}|{book.author}|{book.isbn}|{'1' if book.available else '0'}|{book.borrower_id}"
            for book in self.books
        ]
        user_lines = [
            f"{user.name}|{user.user_id}|{','.join(user.borrowed)}" for user in self.users
        ]
        self._write_atomic(self.books_file, book_lines)
        self._write_atomic(self.users_file, user_lines)

    @staticmethod
    def _write_atomic(path: Path, lines: list[str]) -> None:
        tmp = path.with_name(path.name + ".tmp")
        content = "\n".join(lines)
        if lines:
            content += "\n"
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)

    # ------------------------------------------------------------- recherche
    def find_book(self, isbn: str) -> Book | None:
        return next((book for book in self.books if book.isbn == isbn), None)

    def find_user(self, user_id: str) -> User | None:
        return next((user for user in self.users if user.user_id == user_id), None)

    def search(self, query: str = "") -> list[Book]:
        needle = query.strip().casefold()
        if not needle:
            return list(self.books)
        return [
            book
            for book in self.books
            if needle in book.title.casefold() or needle in book.author.casefold()
        ]

    @property
    def stats(self) -> dict[str, int]:
        available = sum(1 for book in self.books if book.available)
        return {
            "books": len(self.books),
            "available": available,
            "borrowed": len(self.books) - available,
            "users": len(self.users),
        }

    # ------------------------------------------------------------- mutations
    def add_book(self, title: str, author: str, isbn: str) -> Book:
        title = _validate(title, "Titre")
        author = _validate(author, "Auteur")
        isbn = _validate(isbn, "ISBN")
        if self.find_book(isbn):
            raise StoreError(f"Un livre avec l'ISBN {isbn} existe déjà.")
        book = Book(title, author, isbn)
        self.books.append(book)
        return book

    def remove_book(self, isbn: str) -> None:
        book = self.find_book(isbn)
        if book is None:
            raise StoreError("Livre introuvable.")
        self.books.remove(book)
        # Contrairement au C++, on nettoie aussi la liste des emprunteurs
        # pour éviter des ISBN orphelins.
        for user in self.users:
            if isbn in user.borrowed:
                user.borrowed.remove(isbn)

    def add_user(self, name: str, user_id: str) -> User:
        name = _validate(name, "Nom")
        user_id = _validate(user_id, "Identifiant")
        if self.find_user(user_id):
            raise StoreError(f"Un utilisateur avec l'identifiant {user_id} existe déjà.")
        user = User(name, user_id)
        self.users.append(user)
        return user

    def checkout(self, isbn: str, user_id: str) -> Book:
        book = self.find_book(isbn)
        user = self.find_user(user_id)
        if book is None:
            raise StoreError("Livre introuvable.")
        if user is None:
            raise StoreError("Utilisateur introuvable.")
        if not book.available:
            raise StoreError("Ce livre est déjà emprunté.")
        book.available = False
        book.borrower_id = user.user_id
        if isbn not in user.borrowed:
            user.borrowed.append(isbn)
        return book

    def return_book(self, isbn: str) -> Book:
        book = self.find_book(isbn)
        if book is None:
            raise StoreError("Livre introuvable.")
        if book.available:
            raise StoreError("Ce livre n'est pas emprunté.")
        book.available = True
        book.borrower_id = ""
        for user in self.users:
            if isbn in user.borrowed:
                user.borrowed.remove(isbn)
        return book
