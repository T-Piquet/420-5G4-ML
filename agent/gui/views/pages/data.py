"""Page des données et copies de secours."""
from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui.views import theme
from gui.views.table import CellKind, Column, DataTable
from gui.views.widgets import PageHeader, Panel, make_button, make_label

_COLUMNS = (Column("Fichier", 4, max_chars=50), Column("État", 2, CellKind.STATUS))


def _noop() -> None:
    pass


class DataPage(ctk.CTkScrollableFrame):
    def __init__(self, master) -> None:
        super().__init__(
            master, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=theme.SCROLLBAR, scrollbar_button_hover_color=theme.MUTED,
        )
        self.grid_columnconfigure(0, weight=1)
        self.on_save: Callable[[], None] = _noop
        self.on_backup: Callable[[], None] = _noop
        self.on_reload: Callable[[], None] = _noop

        self._header = PageHeader(self, "Données", "")
        self._header.grid(row=0, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(16, 16))

        files = Panel(self, "Fichiers")
        files.grid(row=1, column=0, sticky="ew", padx=theme.PAGE_PADDING)
        self._files = DataTable(files, _COLUMNS, scrollable=False)
        self._files.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 10))

        actions = Panel(self, "Actions")
        actions.grid(row=2, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=18)
        for row, (title, text, label, handler, variant) in enumerate((
            ("Enregistrer", "Écrit vos changements dans books.txt et users.txt.",
             "Enregistrer les données", lambda: self.on_save(), "primary"),
            ("Copie de secours", "Copie les fichiers déjà enregistrés et remplace la copie précédente.",
             "Créer une copie", lambda: self.on_backup(), "secondary"),
            ("Revenir en arrière", "Efface vos changements et revient au dernier enregistrement.",
             "Annuler mes modifications", lambda: self.on_reload(), "secondary"),
        ), start=1):
            line = ctk.CTkFrame(actions, fg_color="transparent")
            line.grid(row=row, column=0, sticky="ew", padx=22, pady=(0, 14))
            line.grid_columnconfigure(0, weight=1)
            make_label(line, title, "strong", theme.INK, anchor="w").grid(row=0, column=0, sticky="w")
            make_label(line, text, "small", theme.MUTED, anchor="w").grid(row=1, column=0, sticky="w")
            make_button(line, label, handler, variant, width=210).grid(row=0, column=1, rowspan=2)

    def show_location(self, location: str) -> None:
        self._header.subtitle.configure(text=location)

    def show_files(self, rows: Sequence[Sequence]) -> None:
        self._files.set_rows(rows)
