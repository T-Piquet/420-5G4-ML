"""Lecture et écriture des fichiers de données de la bibliothèque."""

from __future__ import annotations

from pathlib import Path

from app.models.library import Library, require_native


class LibraryRepository:
    """Accès aux fichiers books.txt et users.txt via le FileManager C++."""

    def __init__(self, data_dir: Path | str) -> None:
        native = require_native()
        self.data_dir = Path(data_dir)
        self.books_path = self.data_dir / "books.txt"
        self.users_path = self.data_dir / "users.txt"
        self._file_manager = native.FileManager(
            str(self.books_path),
            str(self.users_path),
        )

    def load(self) -> Library:
        """Charge les livres et les utilisateurs, ou renvoie une bibliothèque vide."""
        library = Library()
        # False signifie ici « aucun fichier trouvé », pas une erreur.
        self._file_manager.load_library(library.native)
        return library

    def save(self, library: Library) -> None:
        """Écrit les deux fichiers de façon atomique via le C++."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            saved = self._file_manager.save_library(library.native)
        except Exception as error:  # pragma: no cover - dépend du système
            raise OSError(
                "Impossible d'enregistrer les données de la bibliothèque."
            ) from error

        if not saved:
            raise OSError(
                "Impossible d'enregistrer les données de la bibliothèque."
            )

    def create_backup(self) -> None:
        """Copie les fichiers actuels en `.backup` via le C++."""
        try:
            created = self._file_manager.create_backup()
        except Exception as error:  # pragma: no cover - dépend du système
            raise OSError("Impossible de créer la sauvegarde.") from error

        if not created:
            raise OSError("Impossible de créer la sauvegarde.")
