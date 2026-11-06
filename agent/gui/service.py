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


class LibraryError(Exception):
    """Erreur metier destinee a etre affichee telle quelle dans l'interface."""


def _clean_field(value: str, label: str) -> str:
    """Nettoie un champ de saisie et refuse les valeurs qui corrompent les fichiers."""
    text = (value or "").strip()
    if not text:
        raise LibraryError(f"Le champ « {label} » est obligatoire.")
    if any(char in text for char in ("|", "\n", "\r")):
        raise LibraryError(
            f"Le champ « {label} » ne peut pas contenir « | » "
            "ni de retour à la ligne."
        )
    return text


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
        self.data_dir.mkdir(parents=True, exist_ok=True)
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

    def get_available_books(self) -> list[BookView]:
        return [book for book in self.get_books() if book.available]

    # ------------------------------------------------------------------
    # Mutations — chaque operation reussie est suivie d'une sauvegarde.
    # ------------------------------------------------------------------

    def _autosave(self) -> None:
        try:
            saved = self.file_manager.saveLibraryData(self.library)
        except Exception as exc:
            self.reload()
            raise LibraryError(
                f"Impossible d'enregistrer les données : {exc}"
            ) from exc

        if not saved:
            self.reload()
            raise LibraryError(
                "Impossible d'enregistrer les données dans "
                f"« {self.data_dir} ». Vérifiez les droits d'écriture."
            )

        self.load_error = None

    def _find_book(self, isbn: str) -> BookView | None:
        return next(
            (book for book in self.get_books() if book.isbn == isbn), None
        )

    def _find_user(self, user_id: str) -> UserView | None:
        return next(
            (user for user in self.get_users() if user.user_id == user_id),
            None,
        )

    def add_book(self, title: str, author: str, isbn: str) -> BookView:
        title = _clean_field(title, "Titre")
        author = _clean_field(author, "Auteur")
        isbn = _clean_field(isbn, "ISBN")

        if self._find_book(isbn) is not None:
            raise LibraryError(
                f"Un livre avec l'ISBN « {isbn} » existe déjà."
            )

        self.library.addBook(_cpp.Book(title, author, isbn))
        self._autosave()
        return BookView(
            title=title,
            author=author,
            isbn=isbn,
            available=True,
            borrower_id="",
        )

    def remove_book(self, isbn: str) -> None:
        isbn = _clean_field(isbn, "ISBN")
        book = self._find_book(isbn)
        if book is None:
            raise LibraryError(
                f"Aucun livre ne correspond à l'ISBN « {isbn} »."
            )
        if not book.available:
            raise LibraryError(
                "Impossible de supprimer un livre en cours d'emprunt. "
                "Retournez-le d'abord."
            )

        if not self.library.removeBook(isbn):
            raise LibraryError(
                f"La suppression du livre « {book.title} » a échoué."
            )
        self._autosave()

    def add_user(self, name: str, user_id: str) -> UserView:
        name = _clean_field(name, "Nom")
        user_id = _clean_field(user_id, "Identifiant")

        if self._find_user(user_id) is not None:
            raise LibraryError(
                f"Un adhérent avec l'identifiant « {user_id} » existe déjà."
            )

        self.library.addUser(_cpp.User(name, user_id))
        self._autosave()
        return UserView(
            name=name,
            user_id=user_id,
            borrowed_books=(),
            borrowed_titles=(),
        )

    def checkout_book(self, isbn: str, user_id: str) -> None:
        isbn = _clean_field(isbn, "ISBN")
        user_id = _clean_field(user_id, "Identifiant de l'adhérent")

        book = self._find_book(isbn)
        if book is None:
            raise LibraryError(
                f"Aucun livre ne correspond à l'ISBN « {isbn} »."
            )
        if not book.available:
            borrower = self._find_user(book.borrower_id)
            borrower_name = (
                borrower.name if borrower else book.borrower_id
            )
            details = (
                f" par {borrower_name}" if borrower_name else ""
            )
            raise LibraryError(
                f"Le livre « {book.title} » est déjà emprunté{details}."
            )

        user = self._find_user(user_id)
        if user is None:
            raise LibraryError(
                "Aucun adhérent ne correspond à l'identifiant "
                f"« {user_id} »."
            )

        if not self.library.checkOutBook(isbn, user_id):
            raise LibraryError("L'emprunt n'a pas pu être effectué.")
        self._autosave()

    def return_book(self, isbn: str) -> None:
        isbn = _clean_field(isbn, "ISBN")
        book = self._find_book(isbn)
        if book is None:
            raise LibraryError(
                f"Aucun livre ne correspond à l'ISBN « {isbn} »."
            )
        if book.available:
            raise LibraryError(
                f"Le livre « {book.title} » n'est pas en cours d'emprunt."
            )

        if not self.library.returnBook(isbn):
            raise LibraryError("Le retour du livre a échoué.")
        self._autosave()

    def create_backup(self) -> tuple[str, ...]:
        sources = [
            path
            for path in (self.books_path, self.users_path)
            if path.exists()
        ]
        if not sources:
            raise LibraryError(
                "Aucun fichier de données à sauvegarder."
            )

        existing = [
            Path(str(path) + ".backup")
            for path in sources
            if Path(str(path) + ".backup").exists()
        ]
        if existing:
            names = ", ".join(path.name for path in existing)
            raise LibraryError(
                f"Une sauvegarde existe déjà ({names}). "
                "Supprimez ou déplacez les fichiers .backup avant "
                "d'en créer une nouvelle."
            )

        try:
            self.file_manager.createBackup()
        except Exception as exc:
            raise LibraryError(
                f"Impossible de créer la sauvegarde : {exc}"
            ) from exc

        return tuple(f"{path.name}.backup" for path in sources)
