"""Page des emprunts en cours."""
from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui.views import theme
from gui.views.table import CellKind, Column, DataTable
from gui.views.widgets import PageHeader, Panel

_COLUMNS = (
    Column("Livre", 5, CellKind.TWO_LINES, max_chars=30),
    Column("ISBN", 3),
    Column("Emprunteur", 3, max_chars=24),
    Column("Identifiant", 2),
    Column("Action", 2, CellKind.ACTIONS),
)


def _noop() -> None:
    pass


class LoansPage(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.on_lend: Callable[[], None] = _noop
        self.on_return: Callable[[], None] = _noop

        self._header = PageHeader(self, "Emprunts en cours", "")
        self._header.grid(row=0, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(16, 16))
        self._header.add_action("Retourner un livre", lambda: self.on_return())
        self._header.add_action("Emprunter un livre", lambda: self.on_lend(), "primary")

        panel = Panel(self)
        panel.grid(row=1, column=0, sticky="nsew", padx=theme.PAGE_PADDING, pady=(0, 24))
        panel.grid_rowconfigure(1, weight=1)
        self._table = DataTable(panel, _COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew", padx=2, pady=8)

    def show_loans(self, rows: Sequence[Sequence], empty_text: str, summary: str) -> None:
        self._table.set_rows(rows, empty_text)
        self._header.subtitle.configure(text=summary)
