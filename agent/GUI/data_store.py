"""Adaptateur entre l'interface Python et le moteur C++ (pybind11).

Le moteur `bibliotheque_core` porte l'état, les règles et la persistance.
Ce module ne fait que :
- valider et mettre en forme les saisies de l'utilisateur ;
- traduire les erreurs du moteur en `StoreError` ou `OSError` ;
- exposer les noms attendus par l'interface (`LibraryStore`, `Book`, `User`).
"""

from __future__ import annotations

from pathlib import Path

try:
    import bibliotheque_core as core
except ImportError as exc:  # pragma: no cover - dépend du build C++
    raise ImportError(
        "Module bibliotheque_core introuvable. Construisez-le depuis agent/ avec "
        "cmake -S . -B build -DBUILD_PYTHON_BINDINGS=ON "
        '-DPython_EXECUTABLE="$PWD/GUI/.venv/bin/python" '
        "-Dpybind11_DIR=/usr/lib/cmake/pybind11 puis cmake --build build -j."
    ) from exc


Book = core.Book
User = core.User


class StoreError(Exception):
    """Erreur de validation ou opération impossible sur la bibliothèque."""


def _validate(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise StoreError(f"{label} obligatoire.")
    if "|" in value:
        raise StoreError(f"{label} ne peut pas contenir le caractère « | ».")
    return value


def _normalize_name(name: str) -> str:
    """Nettoie, valide et met en forme le nom d'un utilisateur."""
    name = " ".join(name.split())
    if not name:
        raise StoreError("Le nom est obligatoire.")
    if "|" in name:
        raise StoreError("Le nom ne peut pas contenir le caractère « | ».")
    if any(character.isdigit() for character in name):
        raise StoreError("Le nom ne peut pas contenir de chiffres.")

    def capitalize(word: str) -> str:
        return "-".join(part[:1].upper() + part[1:] for part in word.split("-"))

    return " ".join(capitalize(word) for word in name.split(" "))


class LibraryStore:
    """Façade mince : saisies validées, moteur C++ pour tout le reste."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.books_file = self.data_dir / "books.txt"
        self.users_file = self.data_dir / "users.txt"
        self._library = core.Library()
        self._files = core.FileManager(str(self.books_file), str(self.users_file))

    # ------------------------------------------------------------------ I/O
    def load(self) -> "LibraryStore":
        self._library = core.Library()
        self._files.load_library_data(self._library)
        return self

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self._files.save_library_data(self._library):
            raise OSError("Échec de la sauvegarde des données de la bibliothèque.")

    def create_backup(self) -> bool:
        """Copie les fichiers dans `<fichier>.backup`.

        Renvoie False s'il n'y a aucun fichier à sauvegarder ; lève OSError si
        la copie échoue réellement.
        """
        if not (self.books_file.exists() or self.users_file.exists()):
            return False

        if not self._files.create_backup():
            raise OSError("Échec de la création de la sauvegarde.")
        return True

    # ------------------------------------------------------------- lecture
    @property
    def books(self) -> list[Book]:
        return self._library.books()

    @property
    def users(self) -> list[User]:
        return self._library.users()

    @property
    def available_books(self) -> list[Book]:
        return self._library.available_books()

    def find_book(self, isbn: str) -> Book | None:
        return self._library.find_book(isbn)

    def find_user(self, user_id: str) -> User | None:
        return self._library.find_user(user_id)

    def search(self, query: str = "") -> list[Book]:
        query = query.strip()
        if not query:
            return self._library.books()
        return self._library.search_books(query)

    def filter_books(
        self, query: str = "", availability: str = "all"
    ) -> list[Book]:
        """Livres correspondant à `query`, restreints au filtre demandé.

        `availability` vaut `all` ou `available` ; la sélection des livres
        disponibles vient du moteur C++ (`getAvailableBooks`).
        """
        query = query.strip()

        if not query:
            if availability == "all":
                return self._library.books()
            if availability == "available":
                return self._library.available_books()
            raise ValueError(f"Filtre inconnu : {availability!r}")

        results = self._library.search_books(query)
        if availability == "all":
            return results
        if availability == "available":
            available = {book.isbn for book in self._library.available_books()}
            return [book for book in results if book.isbn in available]
        raise ValueError(f"Filtre inconnu : {availability!r}")

    @property
    def stats(self) -> dict[str, int]:
        return {
            "books": self._library.total_books,
            "available": self._library.available_book_count,
            "borrowed": self._library.checked_out_book_count,
            "users": len(self._library.users()),
        }

    # ------------------------------------------------------------- mutations
    def add_book(self, title: str, author: str, isbn: str) -> Book:
        title = _validate(title, "Titre")
        author = _validate(author, "Auteur")
        isbn = _validate(isbn, "ISBN")
        try:
            return self._library.create_book(title, author, isbn)
        except core.LibraryError as exc:
            raise StoreError(str(exc)) from exc

    def remove_book(self, isbn: str) -> None:
        if not self._library.remove_book(isbn):
            raise StoreError("Livre introuvable.")

    def add_user(self, name: str) -> User:
        name = _normalize_name(name)
        try:
            return self._library.create_user(name)
        except core.LibraryError as exc:
            raise StoreError(str(exc)) from exc

    def remove_user(self, user_id: str) -> None:
        if not self._library.remove_user(user_id):
            raise StoreError(
                "Suppression impossible : utilisateur introuvable ou emprunts en cours."
            )

    def checkout(self, isbn: str, user_id: str) -> Book:
        try:
            return self._library.check_out_book_checked(isbn, user_id)
        except core.LibraryError as exc:
            raise StoreError(str(exc)) from exc

    def return_book(self, isbn: str) -> Book:
        try:
            return self._library.return_book_checked(isbn)
        except core.LibraryError as exc:
            raise StoreError(str(exc)) from exc
