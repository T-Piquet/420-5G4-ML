"""
Model module - Data management using Python lists (memory mode, no C++ server)
"""
import csv
import os
import datetime
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Book:
    """Book entity representation"""
    id: int
    title: str
    isbn: str
    author: str
    year: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "author": self.author,
            "year": self.year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(
            id=data["id"],
            title=data["title"],
            isbn=data["isbn"],
            author=data["author"],
            year=data["year"],
        )


@dataclass
class User:
    """User (member) entity representation"""
    id: int
    name: str
    email: str
    borrowed_books: List[Book] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "borrowed_isbn": [b.isbn for b in self.borrowed_books],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        borrowed = []
        if "borrowed_isbn" in data and data["borrowed_isbn"]:
            for isbn in data["borrowed_isbn"]:
                # Find matching book by ISBN (simplified - should look up actual book)
                pass
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            borrowed_books=borrowed,
        )


@dataclass
class Borrowing:
    """Borrowing record entity"""
    id: int
    book_id: int
    user_id: int
    borrow_date: str
    return_date: Optional[str] = None  # None if not returned yet

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "borrow_date": self.borrow_date,
            "return_date": self.return_date or "",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Borrowing":
        return cls(
            id=data["id"],
            book_id=data["book_id"],
            user_id=data["user_id"],
            borrow_date=data["borrow_date"],
            return_date=data.get("return_date"),
        )


class LibraryModel:
    """
    Model class - manages all library data in memory using Python lists.
    No C++ server connection - pure memory mode with CSV file persistence.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.books: List[Book] = []
        self.users: List[User] = []
        self.borrowings: List[Borrowing] = []
        self._next_book_id = 1
        self._next_user_id = 1
        self._next_borrowing_id = 1

    def load_from_csv(self, books_file: str, users_file: str):
        """Load initial data from CSV files"""
        # Load books
        if books_file and __import__(os).path.exists(books_file):
            with open(books_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='|')
                for row in reader:
                    book = Book(
                        id=int(row['id']),
                        title=row['title'].strip(),
                        isbn=row['isbn'].strip(),
                        author=row['author'].strip(),
                        year=row['year'].strip(),
                    )
                    self.books.append(book)
                    self._next_book_id = max(self._next_book_id, book.id + 1)

        # Load users
        if users_file and __import__(os).path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='|')
                for row in reader:
                    user = User(
                        id=int(row['id']),
                        name=row['name'].strip(),
                        email=row['email,borrowed_isbn1, borrowed_isbn2'].split(',')[0].strip(),
                    )
                    self.users.append(user)
                    self._next_user_id = max(self._next_user_id, user.id + 1)

        # Load borrowings from separate borrowings.csv if exists
        borrowings_file = __import__(os).path.join(self.data_dir, 'borrowings.csv')
        if borrowings_file and __import__(os).path.exists(borrowings_file):
            with open(borrowings_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='|')
                for row in reader:
                    borrowing = Borrowing(
                        id=int(row['id']),
                        book_id=int(row['book_id']),
                        user_id=int(row['user_id']),
                        borrow_date=row['borrow_date'],
                        return_date=row.get('return_date', ''),
                    )
                    self.borrowings.append(borrowing)
                    self._next_borrowing_id = max(self._next_borrowing_id, borrowing.id + 1)

    def save_to_csv(self, books_file: str, users_file: str):
        """Export data to CSV files (compatible with books.txt/users.txt format)"""
        # Save books to books.txt format (pipe-separated)
        if __import__(os).path.exists(books_file):
            with open(books_file, 'w', encoding='utf-8') as f:
                f.write("id|title|isbn|author|year\n")
                for book in self.books:
                    f.write(f"{book.id}|{book.title}|{book.isbn}|{book.author}|{book.year}\n")

        # Save users to users.txt format (pipe-separated)
        if __import__(os).path.exists(users_file):
            with open(users_file, 'w', encoding='utf-8') as f:
                f.write("id|name|email,borrowed_isbn1, borrowed_isbn2\n")
                for user in self.users:
                    # Simplified format - only store basic info
                    borrowed_str = ",".join([b.isbn for b in user.borrowed_books]) or ""
                    f.write(f"{user.id}|{user.name}|{user.email},{borrowed_str}\n")

        # Save borrowings to separate file
        borrowings_file = __import__(os).path.join(self.data_dir, 'borrowings.csv')
        if __import__(os).path.exists(borrowings_file):
            with open(borrowings_file, 'w', encoding='utf-8') as f:
                f.write("id|book_id|user_id|borrow_date|return_date\n")
                for borrowing in self.borrowings:
                    f.write(
                        f"{borrowing.id}|{borrowing.book_id}|{borrowing.user_id}|"
                        f"{borrowing.borrow_date}|{borrowing.return_date or ''}\n"
                    )

    def add_book(self, title: str, isbn: str, author: str, year: str) -> Book:
        """Add a new book"""
        book = Book(
            id=self._next_book_id,
            title=title.strip(),
            isbn=isbn.strip(),
            author=author.strip(),
            year=year.strip() if year else "",
        )
        self.books.append(book)
        self._next_book_id += 1
        return book

    def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """Find book by ISBN"""
        for book in self.books:
            if book.isbn.lower() == isbn.lower():
                return book
        return None

    def search_books(self, query: str) -> List[Book]:
        """Search books by title, author, or ISBN"""
        query_lower = query.lower()
        return [
            book for book in self.books
            if query_lower in book.title.lower() or
               query_lower in book.author.lower() or
               query_lower in book.isbn.lower()
        ]

    def add_user(self, name: str, email: str) -> User:
        """Add a new user (member)"""
        # Extract email from the format "email,borrowed1,borrowed2" if needed
        parts = email.split(',')
        email_clean = parts[0].strip()
        
        user = User(
            id=self._next_user_id,
            name=name.strip(),
            email=email_clean,
            borrowed_books=[]
        )
        self.users.append(user)
        self._next_user_id += 1
        return user

    def search_users(self, query: str) -> List[User]:
        """Search users by name or email"""
        query_lower = query.lower()
        return [
            user for user in self.users
            if query_lower in user.name.lower() or
               query_lower in user.email.lower()
        ]

    def get_active_borrowings(self) -> List[Borrowing]:
        """Get all active borrowings (not yet returned)"""
        return [b for b in self.borrowings if not b.return_date]

    def record_borrowing(
        self, book_id: int, user_id: int, days: int = 14, borrow_date: str = ""
    ) -> Optional[Borrowing]:
        """Record a new borrowing (borrowing action)"""
        # Find books and users
        book = next((b for b in self.books if b.id == book_id), None)
        user = next((u for u in self.users if u.id == user_id), None)

        if not book or not user:
            return None

        # Check if book is already borrowed
        active = self.get_active_borrowings()
        if any(b.book_id == book_id for b in active):
            return None  # Book already on loan

        borrowing = Borrowing(
            id=self._next_borrowing_id,
            book_id=book.id,
            user_id=user.id,
            borrow_date=borrow_date or __import__(datetime).date().strftime("%Y-%m-%d"),
            return_date=None,
        )
        self.borrowings.append(borrowing)

        # Update user's borrowed books list
        user.borrowed_books.append(book)

        self._next_borrowing_id += 1
        return borrowing

    def record_return(self, borrowing_id: int) -> Optional[Borrowing]:
        """Record a book return (return action)"""
        borrowing = next((b for b in self.borrowings if b.id == borrowing_id), None)
        if not borrowing:
            return None

        # Find the user who borrowed it
        user = next((u for u in self.users if u.id == borrowing.user_id), None)
        book = next((b for b in self.books if b.id == borrowing.book_id), None)

        if user and book:
            # Remove from user's borrowed list
            user.borrowed_books = [b for b in user.borrowed_books if b != book]

        borrowing.return_date = __import__(datetime).date().strftime("%Y-%m-%d")
        return borrowing

    def get_book_count(self) -> int:
        """Get total book count"""
        return len(self.books)

    def get_user_count(self) -> int:
        """Get total user count"""
        return len(self.users)

    def get_active_borrowing_count(self) -> int:
        """Get active borrowing count"""
        return len(self.get_active_borrowings())
