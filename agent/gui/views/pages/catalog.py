"""Page du catalogue."""
from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui.views import theme
from gui.views.pages.dashboard import BOOK_SEARCH_CRITERIA
from gui.views.table import CellKind, Column, DataTable
from gui.views.widgets import PageHeader, Panel, SearchBar, make_label, make_segments

FILTER_ALL = "Tous"
FILTER_AVAILABLE = "Disponibles"
_COLUMNS = (
    Column("Titre et auteur", 5, CellKind.TWO_LINES, max_chars=30),
    Column("ISBN", 3),
    Column("Statut", 3, CellKind.STATUS),
    Column("Emprunté par", 3, max_chars=20),
    Column("Actions", 5, CellKind.ACTIONS),
)


def _noop() -> None:
    pass


class CatalogPage(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.on_add_book: Callable[[], None] = _noop
        self.on_search: Callable[[], None] = _noop

        header = PageHeader(self, "Catalogue", "Empruntez, retournez et gérez vos livres.")
        header.grid(row=0, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(16, 16))
        header.add_action("Ajouter un livre", lambda: self.on_add_book(), "primary")

        tools = ctk.CTkFrame(self, fg_color="transparent")
        tools.grid(row=1, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(0, 12))
        tools.grid_columnconfigure(0, weight=1)
        self.search_bar = SearchBar(tools, BOOK_SEARCH_CRITERIA, lambda: self.on_search())
        self.search_bar.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        make_label(tools, "Afficher", "small", theme.MUTED).grid(row=0, column=1, padx=(0, 8))
        self._filter = make_segments(
            tools, [FILTER_ALL, FILTER_AVAILABLE], lambda _value: self.on_search()
        )
        self._filter.grid(row=0, column=2)

        panel = Panel(self)
        panel.grid(row=2, column=0, sticky="nsew", padx=theme.PAGE_PADDING)
        panel.grid_rowconfigure(1, weight=1)
        self._table = DataTable(panel, _COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew", padx=2, pady=8)

        self._count = make_label(self, "", "small", theme.MUTED, anchor="w")
        self._count.grid(row=3, column=0, sticky="w", padx=theme.PAGE_PADDING, pady=(8, 16))

    @property
    def availability_filter(self) -> str:
        return self._filter.get()

    def set_filter_enabled(self, enabled: bool) -> None:
        self._filter.configure(state="normal" if enabled else "disabled")

    def show_books(self, rows: Sequence[Sequence], empty_text: str, count_text: str) -> None:
        self._table.set_rows(rows, empty_text)
        self._count.configure(text=count_text)
