"""Modèle de l'application : façade unique au-dessus de l'API C++."""
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

from gui.models.backend import load_backend
from gui.models.entities import Book, DataFile, Member, Stats

_FILE_SEPARATOR = "|"
_ISBN_LIST_SEPARATOR = ","


class LibraryError(Exception):
    """Opération refusée ; le message s'adresse directement à l'utilisateur."""


def _clean(value: str, label: str, forbidden: str = _FILE_SEPARATOR) -> str:
    text = value.strip()
    if not text:
        raise LibraryError(f"Renseignez le champ « {label} ».")
    invalid = sorted(char for char in set(forbidden) if char in text)
    if invalid or "\n" in text:
        shown = " ".join(invalid) or "retour à la ligne"
        raise LibraryError(f"Retirez ce caractère du champ « {label} » : {shown}")
    return text


class LibraryModel:
    """Expose les opérations de `Library` et `FileManager` à l'application."""

    def __init__(self, data_dir: Path, backend: ModuleType | None = None) -> None:
        self._api = backend or load_backend()
        self.data_dir = Path(data_dir)
        self._books_path = self.data_dir / "books.txt"
        self._users_path = self.data_dir / "users.txt"
        self._files = self._api.FileManager(str(self._books_path), str(self._users_path))
        self._library = self._load_library()
        self._listeners: list[Callable[[], None]] = []
        self.has_unsaved_changes = False

    def subscribe(self, listener: Callable[[], None]) -> None:
        self._listeners.append(listener)

    # Lectures -----------------------------------------------------------------

    def stats(self) -> Stats:
        return Stats(
            total_books=self._library.get_total_books(),
            available_books=self._library.get_available_book_count(),
            loaned_books=self._library.get_checked_out_book_count(),
            members=len(self._library.get_all_users()),
        )

    def books(self) -> list[Book]:
        return self._to_books(self._library.get_all_books())

    def available_books(self) -> list[Book]:
        return self._to_books(self._library.get_available_books())

    def loaned_books(self) -> list[Book]:
        return [book for book in self.books() if not book.available]

    def search_by_title(self, title: str) -> list[Book]:
        return self._to_books(self._library.search_by_title(title))

    def search_by_author(self, author: str) -> list[Book]:
        return self._to_books(self._library.search_by_author(author))

    def find_book(self, isbn: str) -> Book | None:
        book = self._library.find_book_by_isbn(isbn)
        return self._to_book(book) if book is not None else None

    def members(self) -> list[Member]:
        return [self._to_member(user) for user in self._library.get_all_users()]

    def find_member(self, user_id: str) -> Member | None:
        user = self._library.find_user_by_id(user_id)
        return self._to_member(user) if user is not None else None

    def data_files(self) -> list[DataFile]:
        paths = (
            self._books_path,
            self._users_path,
            self._books_path.with_name(f"{self._books_path.name}.backup"),
            self._users_path.with_name(f"{self._users_path.name}.backup"),
        )
        return [DataFile(path.name, self._files.file_exists(str(path))) for path in paths]

    # Modifications ------------------------------------------------------------

    def add_book(self, title: str, author: str, isbn: str) -> Book:
        title = _clean(title, "Titre")
        author = _clean(author, "Auteur")
        isbn = _clean(isbn, "ISBN")
        if self._library.find_book_by_isbn(isbn) is not None:
            raise LibraryError(f"Un livre porte déjà l'ISBN {isbn}. Vérifiez le numéro saisi.")
        self._library.add_book(self._api.Book(title, author, isbn))
        self._mark_changed()
        return self.find_book(isbn)

    def remove_book(self, isbn: str) -> None:
        if not self._library.remove_book(isbn):
            raise LibraryError("Retournez ce livre avant de le supprimer du catalogue.")
        self._mark_changed()

    def add_member(self, name: str, user_id: str) -> Member:
        name = _clean(name, "Nom complet")
        user_id = _clean(user_id, "Identifiant", _FILE_SEPARATOR + _ISBN_LIST_SEPARATOR)
        if self._library.find_user_by_id(user_id) is not None:
            raise LibraryError(f"L'identifiant {user_id} est déjà utilisé. Choisissez-en un autre.")
        self._library.add_user(self._api.User(name, user_id))
        self._mark_changed()
        return self.find_member(user_id)

    def check_out(self, isbn: str, user_id: str) -> None:
        if not self._library.checkout_book(isbn, user_id):
            raise LibraryError("Cet emprunt est impossible : le livre n'est plus disponible.")
        self._mark_changed()

    def return_book(self, isbn: str) -> None:
        if not self._library.return_book(isbn):
            raise LibraryError("Ce livre n'est pas emprunté.")
        self._mark_changed()

    # Persistance --------------------------------------------------------------

    def save(self) -> None:
        if not self._files.save_data(self._library):
            raise LibraryError(f"Écriture impossible dans {self.data_dir}. Vérifiez les permissions.")
        self.has_unsaved_changes = False
        self._notify()

    def create_backup(self) -> None:
        try:
            self._files.create_backup()
        except RuntimeError as error:
            raise LibraryError(
                f"Copie de secours impossible dans {self.data_dir}. Vérifiez les permissions."
            ) from error
        self._notify()

    def reload(self) -> None:
        self._library = self._load_library()
        self.has_unsaved_changes = False
        self._notify()

    # Interne ------------------------------------------------------------------

    def _load_library(self):
        return self._api.create_library(str(self._books_path), str(self._users_path))

    def _mark_changed(self) -> None:
        self.has_unsaved_changes = True
        self._notify()

    def _notify(self) -> None:
        for listener in self._listeners:
            listener()

    def _to_books(self, books) -> list[Book]:
        return [self._to_book(book) for book in books]

    @staticmethod
    def _to_book(book) -> Book:
        return Book(
            title=book.get_title(),
            author=book.get_author(),
            isbn=book.get_isbn(),
            available=book.is_available(),
            borrower_id=book.get_borrower_id(),
        )

    @staticmethod
    def _to_member(user) -> Member:
        return Member(
            name=user.get_name(),
            user_id=user.get_user_id(),
            borrowed_isbns=tuple(user.get_borrowed_books()),
        )
