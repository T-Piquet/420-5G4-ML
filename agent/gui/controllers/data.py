"""Contrôleur des données et copies de secours."""
from gui.controllers.actions import ActionsController
from gui.models.library_model import LibraryModel
from gui.views.pages.data import DataPage
from gui.views.table import Status


_FILE_LABELS = {
    "books.txt": "Catalogue (books.txt)",
    "users.txt": "Utilisateurs (users.txt)",
    "books.txt.backup": "Copie du catalogue (books.txt.backup)",
    "users.txt.backup": "Copie des utilisateurs (users.txt.backup)",
}


class DataController:
    def __init__(self, model: LibraryModel, view: DataPage, actions: ActionsController) -> None:
        self._model = model
        self._view = view
        view.on_save = actions.save
        view.on_backup = actions.create_backup
        view.on_reload = actions.reload

    def refresh(self) -> None:
        self._view.show_location(f"Dossier : {self._model.data_dir.resolve()}")
        self._view.show_files([
            (_FILE_LABELS[file.name], Status("Présent", True) if file.exists else Status("Absent", False))
            for file in self._model.data_files()
        ])
