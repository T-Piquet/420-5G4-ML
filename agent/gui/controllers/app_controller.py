"""Contrôleur principal : navigation, état global et fermeture."""
from gui.controllers.actions import ActionsController
from gui.controllers.catalog import CatalogController
from gui.controllers.dashboard import DashboardController
from gui.controllers.data import DataController
from gui.controllers.loans import LoansController
from gui.controllers.members import MembersController
from gui.models.library_model import LibraryModel
from gui.views.dialogs import ConfirmDialog, DialogButton
from gui.views.main_window import MainWindow


class AppController:
    def __init__(self, model: LibraryModel, window: MainWindow) -> None:
        self._model = model
        self._window = window
        self.actions = ActionsController(model, window)
        self._catalog = CatalogController(model, window.catalog, self.actions)
        self._pages = {
            "dashboard": DashboardController(model, window.dashboard, self.actions, self.navigate),
            "catalog": self._catalog,
            "members": MembersController(model, window.members, self.actions),
            "loans": LoansController(model, window.loans, self.actions),
            "data": DataController(model, window.data, self.actions),
        }
        self._current = "dashboard"

        window.on_navigate = self.navigate
        window.on_save = self.actions.save
        window.on_close = self.close
        window.on_find = self._find_book
        window.sidebar.set_location(f"Dossier : {model.data_dir.resolve().name}/")
        model.subscribe(self._refresh)
        self.navigate("dashboard")

    def navigate(self, page: str) -> None:
        self._current = page
        self._window.show_page(page)
        self._refresh()

    def close(self) -> None:
        if not self._model.has_unsaved_changes:
            self._window.destroy()
            return
        ConfirmDialog(
            self._window, "Enregistrer avant de quitter ?",
            "Vos modifications seront perdues si vous quittez sans enregistrer.",
            [
                DialogButton("Annuler"),
                DialogButton("Quitter sans enregistrer", self._window.destroy, "danger"),
                DialogButton("Enregistrer et quitter", self._save_and_quit, "primary"),
            ],
        )

    def _refresh(self) -> None:
        stats = self._model.stats()
        self._window.sidebar.set_counts({
            "catalog": stats.total_books,
            "members": stats.members,
            "loans": stats.loaned_books,
        })
        self._window.set_save_state(self._model.has_unsaved_changes)
        self._pages[self._current].refresh()

    def _find_book(self) -> None:
        self.navigate("catalog")
        self._catalog.focus_search()

    def _save_and_quit(self) -> None:
        if self.actions.save():
            self._window.destroy()
