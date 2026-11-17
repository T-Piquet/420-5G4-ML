"""Couche applicative autour des classes C++ exposées par pybind11."""

from pathlib import Path

import bibliotheque_py


class LibraryService:
    """Encapsule la bibliothèque C++ et applique les règles de l'interface."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

        if not self.data_dir.is_dir():
            raise FileNotFoundError(
                f"Le répertoire de données « {self.data_dir} » n'existe pas."
            )

        self._library = bibliotheque_py.Library()
        self._files = bibliotheque_py.FileManager(
            str(self.data_dir / "books.txt"),
            str(self.data_dir / "users.txt"),
        )
        self._files.load(self._library)

    # --- Lecture ---------------------------------------------------------

    def books(self):
        return self._library.all_books()

    def users(self):
        return self._library.all_users()

    def find_book(self, isbn: str):
        return self._library.find_book(isbn)

    def find_user_by_id(self, user_id: str):
        return self._library.find_user(user_id)

    def find_user_by_name(self, name: str):
        """Recherche insensible à la casse et aux accents (via casefold)."""
        key = name.strip().casefold()

        if not key:
            return None

        for user in self.users():
            if user.name.strip().casefold() == key:
                return user

        return None

    # --- Écriture --------------------------------------------------------

    def save(self) -> bool:
        return self._files.save(self._library)

    def add_book(self, title: str, author: str, isbn: str):
        title = title.strip()
        author = author.strip()
        isbn = isbn.strip()

        if not title or not author or not isbn:
            return False, "Tous les champs sont obligatoires."

        if self.find_book(isbn) is not None:
            return False, f"Un livre avec l'ISBN « {isbn} » existe déjà."

        self._library.add_book(bibliotheque_py.Book(title, author, isbn))

        if not self.save():
            return False, "Le livre a été ajouté, mais la sauvegarde a échoué."

        return True, ""

    def add_user(self, name: str, user_id: str):
        name = name.strip()
        user_id = user_id.strip()

        if not name or not user_id:
            return False, "Tous les champs sont obligatoires."

        if self.find_user_by_id(user_id) is not None:
            return False, f"Un utilisateur avec le numéro « {user_id} » existe déjà."

        self._library.add_user(bibliotheque_py.User(name, user_id))

        if not self.save():
            return False, "L'utilisateur a été ajouté, mais la sauvegarde a échoué."

        return True, ""

    def checkout(self, isbn: str, person_name: str):
        name = person_name.strip()

        if not name:
            return False, "Veuillez entrer le nom de la personne."

        user = self.find_user_by_name(name)

        if user is None:
            return False, f"Aucun utilisateur nommé « {name} » n'a été trouvé."

        if not self._library.checkout(isbn, user.user_id):
            return False, "Impossible d'emprunter ce livre."

        if not self.save():
            return False, "L'emprunt a été enregistré, mais la sauvegarde a échoué."

        return True, ""

    def return_book(self, isbn: str):
        if not self._library.return_book(isbn):
            return False, "Impossible de retourner ce livre."

        if not self.save():
            return False, "Le retour a été enregistré, mais la sauvegarde a échoué."

        return True, ""
