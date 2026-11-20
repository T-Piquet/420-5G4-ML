from pathlib import Path
from bibliotheque_py import Library, Book, User, FileManager


class ServiceError(Exception):
    """Exception levée pour les erreurs de service."""
    pass


class ValidationError(ServiceError):
    """Exception levée pour les erreurs de validation des entrées."""
    pass


class LibraryService:
    def __init__(self, data_dir):
        self._data_dir = Path(data_dir)
        self._file_manager = self._make_file_manager(self._data_dir)
        self._library = Library()
        self.reload_library_data()

    @staticmethod
    def _make_file_manager(data_dir):
        return FileManager(
            str(data_dir / "books.txt"),
            str(data_dir / "users.txt"),
        )

    @property
    def data_dir(self):
        return self._data_dir

    @property
    def books(self):
        return self._library.get_all_books()

    @property
    def available_books(self):
        return self._library.get_available_books()

    @property
    def checked_out_books(self):
        return [book for book in self._library.get_all_books() if not book.is_available]

    @property
    def users(self):
        return self._library.get_all_users()

    @property
    def stats(self):
        return {
            "total": self._library.total_books(),
            "disponibles": self._library.available_book_count(),
            "empruntes": self._library.checked_out_book_count(),
            "utilisateurs": len(self._library.get_all_users()),
        }

    def find_book_by_isbn(self, isbn: str):
        isbn = isbn.strip()
        if not isbn:
            raise ValidationError("L'ISBN est requis.")
        return self._library.find_book_by_isbn(isbn)

    def find_user_by_id(self, user_id: str):
        user_id = user_id.strip()
        if not user_id:
            raise ValidationError("L'ID utilisateur est requis.")
        return self._library.find_user_by_id(user_id)

    def add_book(self, title: str, author: str, isbn: str):
        """Ajoute un livre à la bibliothèque."""
        title, author, isbn = title.strip(), author.strip(), isbn.strip()
        if not title or not author or not isbn:
            raise ValidationError("Le titre, l'auteur et l'ISBN sont requis.")
        if self._library.find_book_by_isbn(isbn) is not None:
            raise ServiceError(f"Un livre avec l'ISBN {isbn} existe déjà.")
        self._library.add_book(Book(title, author, isbn))

    def remove_book(self, isbn: str):
        """Supprime un livre de la bibliothèque par son ISBN."""
        isbn = isbn.strip()
        if not isbn:
            raise ValidationError("L'ISBN est requis.")
        if not self._library.remove_book(isbn):
            raise ServiceError(f"Le livre avec l'ISBN {isbn} n'existe pas.")

    def search_books_by_title(self, query: str):
        """Recherche des livres par titre."""
        query = query.strip()
        if not query:
            raise ValidationError("La requête de recherche est requise.")
        return self._library.search_books_by_title(query)

    def search_books_by_author(self, query: str):
        """Recherche des livres par auteur."""
        query = query.strip()
        if not query:
            raise ValidationError("La requête de recherche est requise.")
        return self._library.search_books_by_author(query)

    def add_user(self, name: str, user_id: str):
        """Ajoute un utilisateur à la bibliothèque."""
        name, user_id = name.strip(), user_id.strip()
        if not name or not user_id:
            raise ValidationError("Le nom et l'ID utilisateur sont requis.")
        if self._library.find_user_by_id(user_id) is not None:
            raise ServiceError(f"Un utilisateur avec l'ID {user_id} existe déjà.")
        self._library.add_user(User(name, user_id))

    def remove_user(self, user_id: str):
        """Supprime un utilisateur de la bibliothèque."""
        user_id = user_id.strip()
        if not user_id:
            raise ValidationError("L'ID utilisateur est requis.")
        user = self._library.find_user_by_id(user_id)
        if user is None:
            raise ServiceError(f"L'utilisateur avec l'ID {user_id} n'existe pas.")
        if user.borrowed_count > 0:
            raise ServiceError(
                f"L'utilisateur {user_id} doit d'abord rendre ses livres empruntés."
            )
        if not self._library.remove_user(user_id):
            raise ServiceError(f"Impossible de supprimer l'utilisateur {user_id}.")

    def check_out_book(self, isbn: str, user_id: str):
        """Permet à un utilisateur d'emprunter un livre."""
        isbn, user_id = isbn.strip(), user_id.strip()
        if not isbn or not user_id:
            raise ValidationError("L'ISBN et l'ID utilisateur sont requis.")

        book = self._library.find_book_by_isbn(isbn)
        if book is None:
            raise ServiceError(f"Le livre avec l'ISBN {isbn} n'existe pas.")
        user = self._library.find_user_by_id(user_id)
        if user is None:
            raise ServiceError(f"L'utilisateur avec l'ID {user_id} n'existe pas.")
        if not book.is_available:
            raise ServiceError(
                f"Le livre avec l'ISBN {isbn} est déjà emprunté par {book.borrower_id}."
            )

        if not self._library.check_out_book(isbn, user_id):
            raise ServiceError(f"Impossible d'emprunter le livre avec l'ISBN {isbn}.")

    def return_book(self, isbn: str):
        """Permet à un utilisateur de retourner un livre."""
        isbn = isbn.strip()
        if not isbn:
            raise ValidationError("L'ISBN est requis.")

        book = self._library.find_book_by_isbn(isbn)
        if book is None:
            raise ServiceError(f"Le livre avec l'ISBN {isbn} n'existe pas.")
        if book.is_available:
            raise ServiceError(f"Le livre avec l'ISBN {isbn} n'est pas emprunté.")

        if not self._library.return_book(isbn):
            raise ServiceError(f"Impossible de retourner le livre avec l'ISBN {isbn}.")

    def save_library_data(self):
        """Sauvegarde les données de la bibliothèque dans les fichiers."""
        if not self._file_manager.save_library_data(self._library):
            raise ServiceError("Erreur lors de la sauvegarde des données de la bibliothèque.")

    def backup_library_data(self):
        """Crée une sauvegarde des données de la bibliothèque."""
        if not self._file_manager.create_backup():
            raise ServiceError("Erreur lors de la création de la sauvegarde des données de la bibliothèque.")

    def reload_library_data(self):
        """Recharge les données depuis les fichiers."""
        books = self._data_dir / "books.txt"
        users = self._data_dir / "users.txt"
        self._library = Library()
        if not (books.exists() or users.exists()):
            return
        if not self._file_manager.load_library_data(self._library):
            raise ServiceError("Erreur lors du rechargement des données.")

    def change_data_dir(self, new_dir):
        """Change le répertoire de données et recharge les données."""
        if not new_dir:
            raise ValidationError("Le nouveau répertoire de données est requis.")
        new_path = Path(new_dir)
        if not new_path.is_dir():
            raise ValidationError(f"Le répertoire de données {new_path} n'existe pas.")
        self._data_dir = new_path
        self._file_manager = self._make_file_manager(new_path)
        self.reload_library_data()
