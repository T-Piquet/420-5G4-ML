"""Modèle de données et opérations de la bibliothèque."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import shutil
import tempfile


class LibraryError(Exception):
    """Erreur métier présentable à l'utilisateur."""


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    available: bool = True
    borrower_id: str = ""

    @classmethod
    def from_line(cls, line: str) -> "Book":
        parts = line.split("|")
        if len(parts) < 3:
            raise LibraryError(f"Ligne de livre invalide : {line!r}")
        title, author, isbn = (part.strip() for part in parts[:3])
        available = len(parts) < 4 or parts[3].strip() == "1"
        borrower_id = parts[4].strip() if len(parts) > 4 else ""
        if not title or not author or not isbn:
            raise LibraryError(f"Livre incomplet : {line!r}")
        return cls(title, author, isbn, available, borrower_id)

    def to_line(self) -> str:
        return "|".join(
            [
                self.title,
                self.author,
                self.isbn,
                "1" if self.available else "0",
                self.borrower_id,
            ]
        )

    @property
    def status(self) -> str:
        return "Disponible" if self.available else f"Emprunté ({self.borrower_id})"


@dataclass
class User:
    name: str
    user_id: str
    borrowed_books: list[str] = field(default_factory=list)

    @classmethod
    def from_line(cls, line: str) -> "User":
        parts = line.split("|", 2)
        if len(parts) < 2:
            raise LibraryError(f"Ligne d'utilisateur invalide : {line!r}")
        name, user_id = parts[0].strip(), parts[1].strip()
        if not name or not user_id:
            raise LibraryError(f"Utilisateur incomplet : {line!r}")
        raw_books = parts[2] if len(parts) > 2 else ""
        borrowed = [isbn.strip() for isbn in raw_books.split(",") if isbn.strip()]
        return cls(name, user_id, borrowed)

    def to_line(self) -> str:
        return "|".join([self.name, self.user_id, ",".join(self.borrowed_books)])


class Library:
    """Bibliothèque persistée dans deux fichiers texte pipe-delimités."""

    def __init__(self, books_file: Path, users_file: Path) -> None:
        self.books_file = Path(books_file)
        self.users_file = Path(users_file)
        self.books: list[Book] = []
        self.users: list[User] = []

    def load(self) -> None:
        self.books = self._load_books()
        self.users = self._load_users()

    def _load_books(self) -> list[Book]:
        if not self.books_file.exists():
            return []
        books: list[Book] = []
        for number, line in enumerate(
            self.books_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                books.append(Book.from_line(line))
            except LibraryError as exc:
                raise LibraryError(f"{self.books_file.name}, ligne {number} : {exc}") from exc
        return books

    def _load_users(self) -> list[User]:
        if not self.users_file.exists():
            return []
        users: list[User] = []
        for number, line in enumerate(
            self.users_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                users.append(User.from_line(line))
            except LibraryError as exc:
                raise LibraryError(f"{self.users_file.name}, ligne {number} : {exc}") from exc
        return users

    def save(self) -> None:
        self._atomic_write(self.books_file, (book.to_line() for book in self.books))
        self._atomic_write(self.users_file, (user.to_line() for user in self.users))

    @staticmethod
    def _atomic_write(path: Path, lines) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            prefix=f".{path.name}.", dir=path.parent, text=True
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                for line in lines:
                    stream.write(f"{line}\n")
            os.replace(temporary, path)
        except OSError:
            Path(temporary).unlink(missing_ok=True)
            raise

    def create_backup(self) -> list[Path]:
        backups: list[Path] = []
        for source in (self.books_file, self.users_file):
            if not source.exists():
                continue
            destination = source.with_name(f"{source.name}.backup")
            shutil.copy2(source, destination)
            backups.append(destination)
        return backups

    def find_book_by_isbn(self, isbn: str) -> Book | None:
        key = isbn.strip().lower()
        return next((book for book in self.books if book.isbn.lower() == key), None)

    def find_user_by_id(self, user_id: str) -> User | None:
        key = user_id.strip().lower()
        return next((user for user in self.users if user.user_id.lower() == key), None)

    def add_book(self, title: str, author: str, isbn: str) -> Book:
        title, author, isbn = title.strip(), author.strip(), isbn.strip()
        if not title or not author or not isbn:
            raise LibraryError("Le titre, l'auteur et l'ISBN sont obligatoires.")
        if self.find_book_by_isbn(isbn):
            raise LibraryError(f"Un livre avec l'ISBN {isbn} existe déjà.")
        book = Book(title, author, isbn)
        self.books.append(book)
        return book

    def remove_book(self, isbn: str) -> Book:
        book = self.find_book_by_isbn(isbn)
        if not book:
            raise LibraryError(f"Aucun livre trouvé avec l'ISBN {isbn}.")
        self.books.remove(book)
        for user in self.users:
            if book.isbn in user.borrowed_books:
                user.borrowed_books.remove(book.isbn)
        return book

    def add_user(self, name: str, user_id: str) -> User:
        name, user_id = name.strip(), user_id.strip()
        if not name or not user_id:
            raise LibraryError("Le nom et l'identifiant sont obligatoires.")
        if self.find_user_by_id(user_id):
            raise LibraryError(f"Un utilisateur avec l'ID {user_id} existe déjà.")
        user = User(name, user_id)
        self.users.append(user)
        return user

    def search_books_by_title(self, query: str) -> list[Book]:
        key = query.strip().lower()
        if not key:
            return list(self.books)
        return [book for book in self.books if key in book.title.lower()]

    def search_books_by_author(self, query: str) -> list[Book]:
        key = query.strip().lower()
        if not key:
            return list(self.books)
        return [book for book in self.books if key in book.author.lower()]

    def search_books(self, query: str) -> list[Book]:
        key = query.strip().lower()
        if not key:
            return list(self.books)
        return [
            book
            for book in self.books
            if key in book.title.lower()
            or key in book.author.lower()
            or key in book.isbn.lower()
        ]

    def available_books(self) -> list[Book]:
        return [book for book in self.books if book.available]

    def check_out_book(self, isbn: str, user_id: str) -> Book:
        book = self.find_book_by_isbn(isbn)
        if not book:
            raise LibraryError(f"Aucun livre trouvé avec l'ISBN {isbn}.")
        user = self.find_user_by_id(user_id)
        if not user:
            raise LibraryError(f"Aucun utilisateur trouvé avec l'ID {user_id}.")
        if not book.available:
            raise LibraryError(
                f"Le livre « {book.title} » est déjà emprunté par {book.borrower_id}."
            )
        book.available = False
        book.borrower_id = user.user_id
        if book.isbn not in user.borrowed_books:
            user.borrowed_books.append(book.isbn)
        return book

    def return_book(self, isbn: str) -> Book:
        book = self.find_book_by_isbn(isbn)
        if not book:
            raise LibraryError(f"Aucun livre trouvé avec l'ISBN {isbn}.")
        if book.available:
            raise LibraryError(f"Le livre « {book.title} » est déjà disponible.")
        borrower = self.find_user_by_id(book.borrower_id)
        if borrower and book.isbn in borrower.borrowed_books:
            borrower.borrowed_books.remove(book.isbn)
        book.available = True
        book.borrower_id = ""
        return book

    def total_books(self) -> int:
        return len(self.books)

    def available_count(self) -> int:
        return len(self.available_books())

    def checked_out_count(self) -> int:
        return self.total_books() - self.available_count()

    def total_users(self) -> int:
        return len(self.users)

    def borrowed_by(self, user: User) -> list[Book]:
        books = {book.isbn: book for book in self.books}
        return [books[isbn] for isbn in user.borrowed_books if isbn in books]
