"""Modèles de données et chargement des fichiers pipe-séparés."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


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
    borrowed_isbns: list[str] = field(default_factory=list)


FALLBACK_BOOKS = (
    ("Le Petit Prince", "Antoine de Saint-Exupéry", "9782070612758", True, ""),
    ("Les Misérables", "Victor Hugo", "9782253096337", False, "USR001"),
    ("L'Étranger", "Albert Camus", "9782070360024", True, ""),
    ("Madame Bovary", "Gustave Flaubert", "9782070413119", False, "USR002"),
    ("Le Rouge et le Noir", "Stendhal", "9782070411326", True, ""),
    ("Germinal", "Émile Zola", "9782253004226", False, "USR003"),
)

FALLBACK_USERS = (
    ("Marie Dubois", "USR001", ["9782253096337"]),
    ("Jean Martin", "USR002", ["9782070413119"]),
    ("Sophie Lemaire", "USR003", ["9782253004226"]),
    ("Alexandra Dumont", "USR015", []),
)


class LibraryStore:
    """État en mémoire de la bibliothèque, alimenté par les fichiers source."""

    def __init__(self, books: list[Book] | None = None,
                 users: list[User] | None = None):
        self.books: list[Book] = books or []
        self.users: list[User] = users or []

    @classmethod
    def load(cls, data_dir: Path | None = None) -> "LibraryStore":
        directory = data_dir or DATA_DIR
        books = cls._read_books(directory / "books.txt")
        users = cls._read_users(directory / "users.txt")
        return cls(books, users)

    @staticmethod
    def _read_books(path: Path) -> list[Book]:
        books: list[Book] = []
        try:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    parts = line.rstrip("\n").split("|")
                    if len(parts) < 3 or not parts[0].strip():
                        continue
                    books.append(Book(
                        title=parts[0].strip(),
                        author=parts[1].strip() if len(parts) > 1 else "",
                        isbn=parts[2].strip(),
                        available=(len(parts) < 4 or parts[3].strip() == "1"),
                        borrower_id=parts[4].strip() if len(parts) > 4 else "",
                    ))
        except OSError:
            return [Book(*row) for row in FALLBACK_BOOKS]
        return books

    @staticmethod
    def _read_users(path: Path) -> list[User]:
        users: list[User] = []
        try:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    parts = line.rstrip("\n").split("|")
                    if len(parts) < 2 or not parts[0].strip():
                        continue
                    borrowed = parts[2].split(",") if len(parts) > 2 else []
                    users.append(User(
                        name=parts[0].strip(),
                        user_id=parts[1].strip(),
                        borrowed_isbns=[isbn.strip() for isbn in borrowed if isbn.strip()],
                    ))
        except OSError:
            return [User(name, user_id, list(isbns))
                    for name, user_id, isbns in FALLBACK_USERS]
        return users

    def book_by_isbn(self, isbn: str) -> Book | None:
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def user_by_id(self, user_id: str) -> User | None:
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def available_books(self) -> list[Book]:
        return [book for book in self.books if book.available]

    def borrowed_books(self) -> list[Book]:
        return [book for book in self.books if not book.available]

    def ongoing_loans(self) -> list[tuple[Book, User | None]]:
        loans = []
        for book in self.borrowed_books():
            loans.append((book, self.user_by_id(book.borrower_id)))
        loans.sort(key=lambda loan: loan[0].title.casefold())
        return loans

    @property
    def total_books(self) -> int:
        return len(self.books)

    @property
    def available_count(self) -> int:
        return sum(1 for book in self.books if book.available)

    @property
    def borrowed_count(self) -> int:
        return self.total_books - self.available_count

    @property
    def total_users(self) -> int:
        return len(self.users)

    @property
    def availability_rate(self) -> int:
        if not self.books:
            return 0
        return round(self.available_count / self.total_books * 100)

    def add_book(self, book: Book) -> None:
        if not book.title or not book.author or not book.isbn:
            raise ValueError("Titre, auteur et ISBN sont obligatoires.")
        if self.book_by_isbn(book.isbn):
            raise ValueError(f"Un livre avec l'ISBN {book.isbn} existe déjà.")
        self.books.append(book)

    def remove_book(self, book: Book) -> None:
        target = self.book_by_isbn(book.isbn)
        if target is None:
            raise ValueError("Ce livre n'existe pas dans le catalogue.")
        if not target.available:
            user = self.user_by_id(target.borrower_id)
            if user and target.isbn in user.borrowed_isbns:
                user.borrowed_isbns.remove(target.isbn)
        self.books.remove(target)

    def add_user(self, user: User) -> None:
        if not user.name or not user.user_id:
            raise ValueError("Nom et identifiant sont obligatoires.")
        if self.user_by_id(user.user_id):
            raise ValueError(f"L'identifiant {user.user_id} est déjà utilisé.")
        self.users.append(user)

    def borrow(self, book: Book, user: User) -> None:
        if not book.available:
            raise ValueError("Ce livre est déjà emprunté.")
        book.available = False
        book.borrower_id = user.user_id
        if book.isbn not in user.borrowed_isbns:
            user.borrowed_isbns.append(book.isbn)

    def return_book(self, book: Book) -> None:
        if book.available:
            raise ValueError("Ce livre n'est pas emprunté.")
        user = self.user_by_id(book.borrower_id)
        if user and book.isbn in user.borrowed_isbns:
            user.borrowed_isbns.remove(book.isbn)
        book.available = True
        book.borrower_id = ""

    def user_for(self, book: Book) -> User | None:
        return self.user_by_id(book.borrower_id)
