"""Python facade connecting the CustomTkinter GUI to the C++ pybind11 module."""

from dataclasses import dataclass, field
from pathlib import Path
import shutil
from typing import Dict, List, Optional, Tuple

try:
    import bibliotheque_cpp
    HAS_CPP_MODULE = True
except ImportError:
    bibliotheque_cpp = None
    HAS_CPP_MODULE = False


@dataclass
class BookDTO:
    title: str
    author: str
    isbn: str
    is_available: bool = True
    borrower_id: str = ""


@dataclass
class UserDTO:
    name: str
    user_id: str
    borrowed_books: List[str] = field(default_factory=list)


class BibliothequeAPI:
    """Facade around the C++ Library/FileManager, with a Python file fallback if uncompiled."""

    def __init__(self, data_dir: Optional[str] = None, require_cpp: bool = False) -> None:
        base_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "data"
        self.data_dir = base_dir
        self.books_file = base_dir / "books.txt"
        self.users_file = base_dir / "users.txt"
        self.using_cpp = HAS_CPP_MODULE

        if require_cpp and not HAS_CPP_MODULE:
            raise ImportError(
                "Le module C++ 'bibliotheque_cpp' est introuvable. "
                "Compilez-le dans agent/build avec: cmake .. && make"
            )

        if HAS_CPP_MODULE:
            self._library = bibliotheque_cpp.Library()
            self._file_manager = bibliotheque_cpp.FileManager(
                str(self.books_file), str(self.users_file)
            )
            self._file_manager.loadLibraryData(self._library)
        else:
            print(
                "[INFO] Module C++ 'bibliotheque_cpp' non compilé sur cette machine. "
                "Utilisation du mode fallback Python sur data/books.txt et data/users.txt."
            )
            self._books: List[BookDTO] = []
            self._users: List[UserDTO] = []
            self._load_fallback()

    @staticmethod
    def _to_book_dto(book) -> BookDTO:
        return BookDTO(
            title=book.getTitle(),
            author=book.getAuthor(),
            isbn=book.getISBN(),
            is_available=book.getAvailability(),
            borrower_id=book.getBorrowerId(),
        )

    def _load_fallback(self) -> None:
        if self.books_file.exists():
            for line in self.books_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 4:
                    self._books.append(
                        BookDTO(
                            title=parts[0],
                            author=parts[1],
                            isbn=parts[2],
                            is_available=(parts[3] == "1"),
                            borrower_id=parts[4] if len(parts) > 4 else "",
                        )
                    )
        if self.users_file.exists():
            for line in self.users_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 2:
                    borrowed = [b for b in parts[2].split(",") if b] if len(parts) > 2 else []
                    self._users.append(UserDTO(name=parts[0], user_id=parts[1], borrowed_books=borrowed))

    def get_all_books(self) -> List[BookDTO]:
        if self.using_cpp:
            return [self._to_book_dto(b) for b in self._library.getAllBooks()]
        return list(self._books)

    def get_available_books(self) -> List[BookDTO]:
        if self.using_cpp:
            return [self._to_book_dto(b) for b in self._library.getAvailableBooks()]
        return [b for b in self._books if b.is_available]

    def find_book_by_isbn(self, isbn: str) -> Optional[BookDTO]:
        isbn = isbn.strip()
        if self.using_cpp:
            book = self._library.findBookByISBN(isbn)
            return self._to_book_dto(book) if book is not None else None
        return next((b for b in self._books if b.isbn == isbn), None)

    def search_books_by_title(self, title: str) -> List[BookDTO]:
        title = title.strip()
        if self.using_cpp:
            return [self._to_book_dto(b) for b in self._library.searchBooksByTitle(title)]
        q = title.lower()
        return [b for b in self._books if q in b.title.lower()]

    def search_books_by_author(self, author: str) -> List[BookDTO]:
        author = author.strip()
        if self.using_cpp:
            return [self._to_book_dto(b) for b in self._library.searchBooksByAuthor(author)]
        q = author.lower()
        return [b for b in self._books if q in b.author.lower()]

    def add_book(self, title: str, author: str, isbn: str) -> Tuple[bool, str]:
        title, author, isbn = title.strip(), author.strip(), isbn.strip()
        if not title or not author or not isbn:
            return False, "Tous les champs (titre, auteur, ISBN) sont requis."

        if self.using_cpp:
            if self._library.findBookByISBN(isbn) is not None:
                return False, f"Un livre avec l'ISBN {isbn} existe déjà."
            self._library.addBook(bibliotheque_cpp.Book(title, author, isbn))
            return True, f"Livre '{title}' ajouté."

        if any(b.isbn == isbn for b in self._books):
            return False, f"Un livre avec l'ISBN {isbn} existe déjà."
        self._books.append(BookDTO(title=title, author=author, isbn=isbn))
        return True, f"Livre '{title}' ajouté."

    def remove_book(self, isbn: str) -> Tuple[bool, str]:
        if self.using_cpp:
            book = self._library.findBookByISBN(isbn)
            if book is None:
                return False, f"Aucun livre trouvé avec l'ISBN {isbn}."
            if not book.getAvailability():
                return False, "Impossible de supprimer un livre actuellement emprunté."
            if self._library.removeBook(isbn):
                return True, f"Livre ({isbn}) supprimé."
            return False, "Erreur lors de la suppression du livre."

        for i, book in enumerate(self._books):
            if book.isbn == isbn:
                if not book.is_available:
                    return False, "Impossible de supprimer un livre actuellement emprunté."
                self._books.pop(i)
                return True, f"Livre ({isbn}) supprimé."
        return False, f"Aucun livre trouvé avec l'ISBN {isbn}."

    def get_all_users(self) -> List[UserDTO]:
        if self.using_cpp:
            return [
                UserDTO(
                    name=u.getName(),
                    user_id=u.getUserId(),
                    borrowed_books=list(u.getBorrowedBooks()),
                )
                for u in self._library.getAllUsers()
            ]
        return list(self._users)

    def add_user(self, name: str, user_id: str) -> Tuple[bool, str]:
        name, user_id = name.strip(), user_id.strip()
        if not name or not user_id:
            return False, "Le nom et l'ID utilisateur sont requis."

        if self.using_cpp:
            if self._library.findUserById(user_id) is not None:
                return False, f"Un utilisateur avec l'ID {user_id} existe déjà."
            self._library.addUser(bibliotheque_cpp.User(name, user_id))
            return True, f"Utilisateur '{name}' ajouté."

        if any(u.user_id == user_id for u in self._users):
            return False, f"Un utilisateur avec l'ID {user_id} existe déjà."
        self._users.append(UserDTO(name=name, user_id=user_id))
        return True, f"Utilisateur '{name}' ajouté."

    def update_user_name(self, user_id: str, new_name: str) -> Tuple[bool, str]:
        new_name = new_name.strip()
        if not new_name:
            return False, "Le nom ne peut pas être vide."

        if self.using_cpp:
            user = self._library.findUserById(user_id)
            if user is None:
                return False, f"Utilisateur {user_id} introuvable."
            user.setName(new_name)
            return True, f"Utilisateur {user_id} mis à jour."

        for user in self._users:
            if user.user_id == user_id:
                user.name = new_name
                return True, f"Utilisateur {user_id} mis à jour."
        return False, f"Utilisateur {user_id} introuvable."

    def checkout_book(self, isbn: str, user_id: str) -> Tuple[bool, str]:
        isbn, user_id = isbn.strip(), user_id.strip()
        if self.using_cpp:
            book = self._library.findBookByISBN(isbn)
            if book is None:
                return False, f"Livre {isbn} introuvable."
            if not book.getAvailability():
                return False, f"Le livre {isbn} est déjà emprunté."
            if self._library.findUserById(user_id) is None:
                return False, f"Utilisateur {user_id} introuvable."
            if self._library.checkOutBook(isbn, user_id):
                return True, f"Livre {isbn} emprunté par {user_id}."
            return False, "Impossible d'effectuer l'emprunt."

        book = next((b for b in self._books if b.isbn == isbn), None)
        user = next((u for u in self._users if u.user_id == user_id), None)
        if book is None:
            return False, f"Livre {isbn} introuvable."
        if not book.is_available:
            return False, f"Le livre {isbn} est déjà emprunté."
        if user is None:
            return False, f"Utilisateur {user_id} introuvable."
        book.is_available = False
        book.borrower_id = user_id
        if isbn not in user.borrowed_books:
            user.borrowed_books.append(isbn)
        return True, f"Livre {isbn} emprunté par {user_id}."

    def return_book(self, isbn: str) -> Tuple[bool, str]:
        isbn = isbn.strip()
        if self.using_cpp:
            book = self._library.findBookByISBN(isbn)
            if book is None:
                return False, f"Livre {isbn} introuvable."
            if book.getAvailability():
                return False, f"Le livre {isbn} n'est pas emprunté."
            if self._library.returnBook(isbn):
                return True, f"Livre {isbn} retourné."
            return False, "Impossible d'effectuer le retour."

        book = next((b for b in self._books if b.isbn == isbn), None)
        if book is None:
            return False, f"Livre {isbn} introuvable."
        if book.is_available:
            return False, f"Le livre {isbn} n'est pas emprunté."
        for user in self._users:
            if isbn in user.borrowed_books:
                user.borrowed_books.remove(isbn)
                break
        book.is_available = True
        book.borrower_id = ""
        return True, f"Livre {isbn} retourné."

    def get_stats(self) -> Dict[str, int]:
        if self.using_cpp:
            return {
                "total_books": int(self._library.getTotalBooks()),
                "available_books": int(self._library.getAvailableBookCount()),
                "checked_out_books": int(self._library.getCheckedOutBookCount()),
                "total_users": len(self._library.getAllUsers()),
            }
        total = len(self._books)
        available = sum(1 for b in self._books if b.is_available)
        return {
            "total_books": total,
            "available_books": available,
            "checked_out_books": total - available,
            "total_users": len(self._users),
        }

    def create_backup(self) -> Tuple[bool, str]:
        if self.using_cpp:
            try:
                self._file_manager.createBackup()
                return True, "Fichiers de sauvegarde (.backup) créés."
            except Exception as exc:
                return False, f"Erreur lors de la sauvegarde : {exc}"

        try:
            created = False
            if self.books_file.exists():
                shutil.copyfile(self.books_file, str(self.books_file) + ".backup")
                created = True
            if self.users_file.exists():
                shutil.copyfile(self.users_file, str(self.users_file) + ".backup")
                created = True
            if created:
                return True, "Fichiers de sauvegarde (.backup) créés."
            return False, "Aucun fichier de données à sauvegarder."
        except OSError as exc:
            return False, f"Erreur lors de la sauvegarde : {exc}"

    def save(self) -> bool:
        if self.using_cpp:
            return bool(self._file_manager.saveLibraryData(self._library))

        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            book_lines = [
                f"{b.title}|{b.author}|{b.isbn}|{'1' if b.is_available else '0'}|{b.borrower_id}"
                for b in self._books
            ]
            user_lines = [
                f"{u.name}|{u.user_id}|{','.join(u.borrowed_books)}"
                for u in self._users
            ]
            self.books_file.write_text("\n".join(book_lines) + ("\n" if book_lines else ""), encoding="utf-8")
            self.users_file.write_text("\n".join(user_lines) + ("\n" if user_lines else ""), encoding="utf-8")
            return True
        except OSError:
            return False
