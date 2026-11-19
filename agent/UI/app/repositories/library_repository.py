"""Lecture et écriture des fichiers de données de la bibliothèque."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from pathlib import Path

from app.models.book import Book
from app.models.library import Library
from app.models.user import User


class LibraryRepository:
    """Accès aux fichiers books.txt et users.txt du dossier de données."""

    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.books_path = self.data_dir / "books.txt"
        self.users_path = self.data_dir / "users.txt"

    def load(self) -> Library:
        """Charge les livres et les utilisateurs, ou renvoie une bibliothèque vide."""
        return Library(books=self._load_books(), users=self._load_users())

    def save(self, library: Library) -> None:
        """Écrit les deux fichiers de façon atomique."""
        self._write(
            self.books_path,
            (self._format_book(book) for book in library.books),
        )
        self._write(
            self.users_path,
            (self._format_user(user) for user in library.users),
        )

    def _load_books(self) -> list[Book]:
        books: list[Book] = []
        for line in self._read_lines(self.books_path):
            parts = line.split("|")
            if len(parts) < 4:
                continue

            title, author, isbn, available = parts[0], parts[1], parts[2], parts[3]
            borrower_id = parts[4].strip() if len(parts) > 4 else ""
            if not isbn:
                continue

            books.append(
                Book(
                    title=title,
                    author=author,
                    isbn=isbn,
                    available=available.strip() != "0",
                    borrower_id=borrower_id,
                )
            )
        return books

    def _load_users(self) -> list[User]:
        users: list[User] = []
        for line in self._read_lines(self.users_path):
            parts = line.split("|")
            if len(parts) < 2 or not parts[1]:
                continue

            raw_isbns = parts[2] if len(parts) > 2 else ""
            borrowed_isbns = [
                value.strip() for value in raw_isbns.split(",") if value.strip()
            ]
            users.append(
                User(
                    name=parts[0],
                    user_id=parts[1],
                    borrowed_isbns=borrowed_isbns,
                )
            )
        return users

    @staticmethod
    def _read_lines(path: Path) -> list[str]:
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        return [line for line in content.splitlines() if line.strip()]

    @staticmethod
    def _format_book(book: Book) -> str:
        available = "1" if book.available else "0"
        borrower = "" if book.available else book.borrower_id
        return f"{book.title}|{book.author}|{book.isbn}|{available}|{borrower}"

    @staticmethod
    def _format_user(user: User) -> str:
        return f"{user.name}|{user.user_id}|{','.join(user.borrowed_isbns)}"

    @staticmethod
    def _write(path: Path, lines: Iterable[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(lines)
        if content:
            content += "\n"

        descriptor, temporary = tempfile.mkstemp(
            dir=path.parent,
            prefix=f"{path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(
                descriptor, "w", encoding="utf-8", newline="\n"
            ) as handle:
                handle.write(content)
            os.replace(temporary, path)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise
