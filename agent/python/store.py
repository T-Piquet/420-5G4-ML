#!/usr/bin/env python3
"""Application state for the personal-library GUI.

The domain model (Library, Book, User, FileManager) is the original C++ code,
exposed through the pybind11 module ``biblio_core``.  This module owns the
session state (dirty counters, conflicts, backups) and is shared by the
Tkinter interface and the tests.

It has no HTTP or UI code: it is importable and testable on its own.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "build") not in sys.path:
    sys.path.insert(0, str(ROOT / "build"))

try:
    import biblio_core  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - startup guard
    raise SystemExit(
        "Le module biblio_core est introuvable. Compilez d'abord :\n"
        "  cmake -S agent -B agent/build -G Ninja && cmake --build agent/build\n"
        f"({exc})"
    )

BOOKS_NAME = "books.txt"
USERS_NAME = "users.txt"


class ApiError(Exception):
    """A user-facing failure, optionally tied to a form field."""

    def __init__(self, message: str, status: int = 400, code: str = "invalid",
                 field: str | None = None, extra: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.field = field
        self.extra = extra or {}


def normalise_isbn(raw: str) -> str:
    return "".join(ch for ch in raw if ch not in " -")


def valid_isbn(isbn: str) -> bool:
    return len(isbn) == 13 and isbn.isdigit()


def _french_publisher_length(code: str) -> int:
    """Length of the publisher prefix inside ISBN group 2 (French)."""
    if not code.isdigit():
        return 0
    value = int(code[:2])
    if 0 <= value <= 19:
        return 2
    value = int(code[:3])
    if 200 <= value <= 349 or 400 <= value <= 699 or 900 <= value <= 949:
        return 3
    value = int(code[:4])
    if 7000 <= value <= 8399:
        return 4
    return 0


def format_isbn(isbn: str) -> str:
    """Pretty ISBN for the detail card (French registration group)."""
    if len(isbn) != 13 or not isbn.isdigit() or not isbn.startswith("9782"):
        return isbn
    code = isbn[4:]
    length = _french_publisher_length(code)
    if not length:
        return isbn
    publisher = code[:length]
    title = code[length:8]
    return f"{isbn[0:3]}-{isbn[3]}-{publisher}-{title}-{isbn[12]}"


class Store:
    """Application state over the C++ model.  Not thread safe by itself."""

    def __init__(self, data_dir: Path | None):
        self.data_dir: Path | None = None
        self.books_file: Path | None = None
        self.users_file: Path | None = None
        self.library = None
        self.files = None
        self.dirty = False
        self.added_books = 0
        self.added_users = 0
        self.edited_books = 0
        self.loan_ops = 0
        self.ignored_conflicts: set[str] = set()
        if data_dir is not None:
            self.open_dir(data_dir)

    # ------------------------------------------------------------------ data
    def open_dir(self, directory: Path, create: bool = False) -> None:
        directory = directory.expanduser()
        if create:
            directory.mkdir(parents=True, exist_ok=True)
        if not directory.is_dir():
            raise ApiError(f"Le dossier « {directory} » est introuvable.",
                           code="no_dir", field="dataDir")
        self.data_dir = directory.resolve()
        self.books_file = self.data_dir / BOOKS_NAME
        self.users_file = self.data_dir / USERS_NAME
        self.library = biblio_core.Library()
        self.files = biblio_core.FileManager(str(self.books_file), str(self.users_file))
        self.files.load_library_data(self.library)
        self.dirty = False
        self.added_books = self.added_users = self.edited_books = self.loan_ops = 0
        self.ignored_conflicts = set()

    def _require_open(self) -> None:
        if self.library is None:
            raise ApiError("Aucun dossier de données n'est ouvert.", code="no_data_dir")

    def _touch(self) -> None:
        self.dirty = True

    # -------------------------------------------------------------- snapshots
    def _users_by_id(self) -> dict[str, Any]:
        return {user.user_id: user for user in self.library.all_users()}

    def state(self) -> dict[str, Any]:
        if self.library is None:
            return {
                "needsDataDir": True,
                "dataDir": None,
                "files": [],
                "books": [],
                "users": [],
                "loans": [],
                "stats": {"total": 0, "available": 0, "checkedOut": 0,
                          "users": 0, "usersWithLoans": 0},
                "authors": [],
                "conflicts": [],
                "dirty": False,
                "changes": {"addedBooks": 0, "addedUsers": 0, "editedBooks": 0,
                        "loanOps": 0, "total": 0},
                "backupExists": False,
            }

        books = self.library.all_books()
        users = self.library.all_users()
        users_by_id = {user.user_id: user for user in users}
        books_by_isbn = {book.isbn: book for book in books}

        book_rows = []
        loans = []
        for book in books:
            borrower = users_by_id.get(book.borrower_id) if book.borrower_id else None
            row = {
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "isbnFormatted": format_isbn(book.isbn),
                "available": bool(book.available),
                "borrowerId": book.borrower_id or "",
                "borrowerName": borrower.name if borrower else "",
            }
            book_rows.append(row)
            if book.borrower_id:
                loans.append({
                    "isbn": book.isbn, "title": book.title, "author": book.author,
                    "userId": book.borrower_id,
                    "userName": borrower.name if borrower else "Utilisateur inconnu",
                })

        user_rows = []
        for user in users:
            borrowed = list(user.borrowed_books)
            user_rows.append({
                "id": user.user_id,
                "name": user.name,
                "borrowed": borrowed,
                "borrowCount": len(borrowed),
                "books": [
                    {
                        "isbn": isbn,
                        "title": books_by_isbn[isbn].title if isbn in books_by_isbn else "Livre inconnu",
                        "author": books_by_isbn[isbn].author if isbn in books_by_isbn else "",
                    }
                    for isbn in borrowed
                ],
            })

        authors: dict[str, int] = {}
        for book in books:
            authors[book.author] = authors.get(book.author, 0) + 1
        author_rows = [
            {"name": name, "count": count}
            for name, count in sorted(authors.items(), key=lambda item: -item[1])[:5]
        ]

        return {
            "needsDataDir": False,
            "dataDir": str(self.data_dir),
            "files": [BOOKS_NAME, USERS_NAME],
            "books": book_rows,
            "users": user_rows,
            "loans": loans,
            "stats": {
                "total": len(book_rows),
                "available": sum(1 for b in book_rows if b["available"]),
                "checkedOut": sum(1 for b in book_rows if not b["available"]),
                "users": len(user_rows),
                "usersWithLoans": sum(1 for u in user_rows if u["borrowCount"] > 0),
            },
            "authors": author_rows,
            "conflicts": self.conflicts(),
            "dirty": self.dirty,
            "changes": {
                "addedBooks": self.added_books,
                "addedUsers": self.added_users,
                "editedBooks": self.edited_books,
                "loanOps": self.loan_ops,
                "total": self.added_books + self.added_users + self.edited_books + self.loan_ops,
            },
            "backupExists": self._backup_exists(),
        }

    def conflicts(self) -> list[dict[str, Any]]:
        """Contradictions between books.txt and users.txt, grouped per user.

        The seed data contains the case described by the specification: the
        book *Indiana* is marked as lent to USR010, while USR010's own list
        says *Corinne*.  Both sides are reported in one conflict so the
        dialog can offer the two reparations.
        """
        self._require_open()
        books = {book.isbn: book for book in self.library.all_books()}
        users = {user.user_id: user for user in self.library.all_users()}
        found: list[dict[str, Any]] = []

        for user in users.values():
            claimed = set(user.borrowed_books)
            held = {isbn for isbn, book in books.items() if book.borrower_id == user.user_id}
            if claimed == held:
                continue
            conflict_id = f"mismatch:{user.user_id}"
            if conflict_id in self.ignored_conflicts:
                continue
            extra_book = next(iter(held - claimed), "")
            extra_user = next(iter(claimed - held), "")
            found.append({
                "id": conflict_id,
                "kind": "mismatch",
                "userId": user.user_id,
                "userName": user.name,
                "bookIsbn": extra_book,
                "bookTitle": books[extra_book].title if extra_book else "",
                "userIsbn": extra_user,
                "userTitle": books[extra_user].title if extra_user else "",
            })

        for isbn, book in books.items():
            if book.borrower_id and book.borrower_id not in users:
                conflict_id = f"missing_user:{isbn}"
                if conflict_id in self.ignored_conflicts:
                    continue
                found.append({
                    "id": conflict_id, "kind": "missing_user",
                    "userId": book.borrower_id, "userName": "",
                    "bookIsbn": isbn, "bookTitle": book.title,
                    "userIsbn": "", "userTitle": "",
                })

        for user in users.values():
            for isbn in user.borrowed_books:
                if isbn not in books:
                    conflict_id = f"missing_book:{user.user_id}:{isbn}"
                    if conflict_id in self.ignored_conflicts:
                        continue
                    found.append({
                        "id": conflict_id, "kind": "missing_book",
                        "userId": user.user_id, "userName": user.name,
                        "bookIsbn": "", "bookTitle": "",
                        "userIsbn": isbn, "userTitle": "Livre inconnu",
                    })
        return found

    def _backup_exists(self) -> bool:
        if self.books_file is None:
            return False
        return self.books_file.with_name(self.books_file.name + ".backup").exists() and \
            self.users_file.with_name(self.users_file.name + ".backup").exists()

    # --------------------------------------------------------------- actions
    def add_book(self, title: str, author: str, isbn: str) -> dict[str, Any]:
        self._require_open()
        title = (title or "").strip()
        author = (author or "").strip()
        isbn = normalise_isbn(isbn or "")
        if not title:
            raise ApiError("Le titre est obligatoire.", field="title")
        if not author:
            raise ApiError("L'auteur est obligatoire.", field="author")
        if "|" in title or "|" in author:
            raise ApiError("Le caractère « | » n'est pas permis.", field="title")
        if not valid_isbn(isbn):
            raise ApiError("L'ISBN doit contenir 13 chiffres (tirets et espaces ignorés).",
                           field="isbn")
        existing = self.library.find_book(isbn)
        if existing is not None:
            raise ApiError("Cet ISBN est déjà présent dans la bibliothèque.",
                           code="duplicate_isbn", field="isbn",
                           extra={"existingIsbn": isbn, "existingTitle": existing.title})
        self.library.add_book(biblio_core.Book(title, author, isbn))
        self.added_books += 1
        self._touch()
        return self.state()

    def update_book(self, isbn: str, title: str, author: str) -> dict[str, Any]:
        self._require_open()
        book = self.library.find_book(normalise_isbn(isbn))
        if book is None:
            raise ApiError("Livre introuvable.", status=404, code="not_found")
        title = (title or "").strip()
        author = (author or "").strip()
        if not title:
            raise ApiError("Le titre est obligatoire.", field="title")
        if not author:
            raise ApiError("L'auteur est obligatoire.", field="author")
        if "|" in title or "|" in author:
            raise ApiError("Le caractère « | » n'est pas permis.", field="title")
        book.set_title(title)
        book.set_author(author)
        self.edited_books += 1
        self._touch()
        return self.state()

    def remove_book(self, isbn: str, return_first: bool = False) -> dict[str, Any]:
        self._require_open()
        isbn = normalise_isbn(isbn)
        book = self.library.find_book(isbn)
        if book is None:
            raise ApiError("Livre introuvable.", status=404, code="not_found")
        if not book.available and not return_first:
            user = self.library.find_user(book.borrower_id)
            raise ApiError(
                "Ce livre est emprunté : il faut d'abord le retourner.",
                status=409, code="borrowed",
                extra={"borrowerId": book.borrower_id,
                       "borrowerName": user.name if user else "Utilisateur inconnu"},
            )
        if return_first and not book.available:
            user = self.library.find_user(book.borrower_id)
            if user is not None:
                user.return_book(isbn)
            book.return_book()
            self.loan_ops += 1
        self.library.remove_book(isbn)
        self._touch()
        return self.state()

    def add_user(self, name: str) -> dict[str, Any]:
        self._require_open()
        name = (name or "").strip()
        if not name:
            raise ApiError("Le nom est obligatoire.", field="name")
        if "|" in name:
            raise ApiError("Le caractère « | » n'est pas permis.", field="name")
        numbers = []
        for user in self.library.all_users():
            suffix = user.user_id[3:] if user.user_id.startswith("USR") else ""
            if suffix.isdigit():
                numbers.append(int(suffix))
        next_id = f"USR{max(numbers, default=0) + 1:03d}"
        self.library.add_user(biblio_core.User(name, next_id))
        self.added_users += 1
        self._touch()
        return self.state()

    def check_out(self, isbn: str, user_id: str) -> dict[str, Any]:
        self._require_open()
        isbn = normalise_isbn(isbn)
        book = self.library.find_book(isbn)
        if book is None:
            raise ApiError("Livre introuvable.", status=404, code="not_found")
        if not book.available:
            raise ApiError("Ce livre est déjà emprunté.", status=409, code="unavailable")
        user = self.library.find_user(user_id)
        if user is None:
            raise ApiError("Utilisateur introuvable.", status=404, code="unknown_user")
        self.library.check_out_book(isbn, user_id)
        self.loan_ops += 1
        self._touch()
        return self.state()

    def return_loan(self, isbn: str) -> dict[str, Any]:
        self._require_open()
        isbn = normalise_isbn(isbn)
        book = self.library.find_book(isbn)
        if book is None:
            raise ApiError("Livre introuvable.", status=404, code="not_found")
        if book.available:
            raise ApiError("Ce livre est déjà sur l'étagère.", status=409, code="available")
        self.library.return_book(isbn)
        self.loan_ops += 1
        self._touch()
        return self.state()

    def reconcile(self, user_id: str, isbn: str, keep: str) -> dict[str, Any]:
        self._require_open()
        user_id = user_id or ""
        isbn = normalise_isbn(isbn or "")
        if keep == "ignore":
            # Remember the dismissal for this session; the conflict stays in
            # the files but no longer interrupts the user.
            for conflict in self.conflicts():
                if (user_id and conflict["userId"] == user_id) or \
                        (isbn and conflict["bookIsbn"] == isbn):
                    self.ignored_conflicts.add(conflict["id"])
            return self.state()

        user = self.library.find_user(user_id) if user_id else None

        if keep in ("book", "user") and user is None:
            raise ApiError("Utilisateur introuvable.", status=404, code="unknown_user")

        if keep in ("book", "user"):
            books = {b.isbn: self.library.find_book(b.isbn)
                     for b in self.library.all_books()}
            claimed = set(user.borrowed_books)
            held = {i for i, book in books.items() if book.borrower_id == user_id}
            if keep == "book":
                for extra in claimed - held:
                    user.return_book(extra)
                for missing in held - claimed:
                    user.borrow_book(missing)
            else:
                for wanted in claimed:
                    book = books.get(wanted)
                    if book is None:
                        continue
                    if book.available:
                        book.check_out(user_id)
                    elif book.borrower_id != user_id:
                        book.set_borrower_id(user_id)
                for extra in held - claimed:
                    books[extra].return_book()
            self._touch()
            return self.state()

        book = self.library.find_book(isbn) if isbn else None
        if keep == "return" and book is not None:
            book.return_book()
            self._touch()
            return self.state()
        if keep == "drop" and user is not None:
            user.return_book(isbn)
            self._touch()
            return self.state()

        raise ApiError("Choix de résolution invalide.", field="keep")

    def save(self) -> dict[str, Any]:
        self._require_open()
        ok = self.files.save_library_data(self.library)
        if not ok:
            raise ApiError(f"Impossible d'écrire dans {self.data_dir}.",
                           status=500, code="write_failed")
        self.dirty = False
        self.added_books = self.added_users = self.edited_books = self.loan_ops = 0
        self.ignored_conflicts = set()
        return self.state()

    def backup(self, mode: str) -> dict[str, Any]:
        self._require_open()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        written = []
        for source in (self.books_file, self.users_file):
            if source is None or not source.exists():
                continue
            if mode == "dated":
                target = source.with_name(f"{source.name}.backup-{stamp}")
            elif mode == "replace":
                target = source.with_name(f"{source.name}.backup")
            else:
                raise ApiError("Mode de sauvegarde invalide.", field="mode")
            shutil.copy2(source, target)
            written.append(target.name)
        if not written:
            raise ApiError("Aucun fichier de données à sauvegarder.", code="no_files")
        state = self.state()
        state["backupFiles"] = written
        state["backupMode"] = mode
        return state
