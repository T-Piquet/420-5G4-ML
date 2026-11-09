"""Page des utilisateurs."""
from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui.views import theme
from gui.views.table import CellKind, Column, DataTable
from gui.views.widgets import PageHeader, Panel, SearchBar, SearchCriterion, make_label

_COLUMNS = (
    Column("Utilisateur", 4),
    Column("Identifiant", 2),
    Column("Livres empruntés", 2),
    Column("Action", 2, CellKind.ACTIONS),
)
_SEARCH = [SearchCriterion("Identifiant", "Saisir l'identifiant complet, puis Entrée", live=False)]


def _noop() -> None:
    pass


class MembersPage(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.on_add_member: Callable[[], None] = _noop
        self.on_search: Callable[[], None] = _noop

        header = PageHeader(self, "Utilisateurs", "Les personnes inscrites à votre bibliothèque.")
        header.grid(row=0, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(16, 16))
        header.add_action("Ajouter un utilisateur", lambda: self.on_add_member(), "primary")

        self.search_bar = SearchBar(self, _SEARCH, lambda: self.on_search())
        self.search_bar.grid(row=1, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(0, 12))

        panel = Panel(self)
        panel.grid(row=2, column=0, sticky="nsew", padx=theme.PAGE_PADDING)
        panel.grid_rowconfigure(1, weight=1)
        self._table = DataTable(panel, _COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew", padx=2, pady=8)

        self._count = make_label(self, "", "small", theme.MUTED, anchor="w")
        self._count.grid(row=3, column=0, sticky="w", padx=theme.PAGE_PADDING, pady=(8, 16))

    def show_members(self, rows: Sequence[Sequence], empty_text: str, count_text: str) -> None:
        self._table.set_rows(rows, empty_text)
        self._count.configure(text=count_text)
