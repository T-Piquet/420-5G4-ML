"""Page d'accueil : rayon, chiffres clés, aperçu et actions rapides."""
from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui.views import theme
from gui.views.shelf import Shelf, Spine
from gui.views.table import CellKind, Column, DataTable
from gui.views.widgets import (
    PageHeader,
    Panel,
    SearchBar,
    SearchCriterion,
    make_button,
    make_label,
)

_COLUMNS = (
    Column("Livre", 5, CellKind.TWO_LINES, max_chars=24),
    Column("ISBN", 4),
    Column("Statut", 3, CellKind.STATUS),
    Column("Action", 3, CellKind.ACTIONS),
)
BOOK_SEARCH_CRITERIA = [
    SearchCriterion("Titre", "Rechercher dans les titres", live=True),
    SearchCriterion("Auteur", "Rechercher un auteur", live=True),
    SearchCriterion("ISBN", "Saisir l'ISBN complet, puis Entrée", live=False),
]


def _noop() -> None:
    pass


class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master) -> None:
        super().__init__(
            master, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=theme.SCROLLBAR, scrollbar_button_hover_color=theme.MUTED,
        )
        self.grid_columnconfigure(0, weight=1)
        self.on_add_book: Callable[[], None] = _noop
        self.on_open_catalog: Callable[[], None] = _noop
        self.on_lend: Callable[[], None] = _noop
        self.on_return: Callable[[], None] = _noop
        self.on_add_member: Callable[[], None] = _noop
        self.on_save: Callable[[], None] = _noop
        self.on_search: Callable[[], None] = _noop

        header = PageHeader(self, "Votre bibliothèque", "Vos livres, vos emprunts et vos utilisateurs en un coup d'œil.")
        header.grid(row=0, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(16, 18))
        header.add_action("Voir le catalogue", lambda: self.on_open_catalog())
        header.add_action("Ajouter un livre", lambda: self.on_add_book(), "primary")

        self._build_overview()
        self._build_lower_panels()

    def _build_overview(self) -> None:
        panel = Panel(self, "Vos livres", "En couleur : disponibles. En pointillé : empruntés.")
        panel.grid(row=1, column=0, sticky="ew", padx=theme.PAGE_PADDING)
        self._shelf = Shelf(panel)
        self._shelf.grid(row=1, column=0, sticky="ew", padx=22)
        figures = ctk.CTkFrame(panel, fg_color="transparent")
        figures.grid(row=2, column=0, sticky="ew", padx=22, pady=(14, 18))
        self._figures: list[tuple[ctk.CTkLabel, ctk.CTkLabel]] = []
        for index in range(4):
            figures.grid_columnconfigure(index, weight=1, uniform="figures")
            value = make_label(figures, "", "figure", theme.INK, anchor="w")
            caption = make_label(figures, "", "small", theme.MUTED, anchor="w")
            value.grid(row=0, column=index, sticky="w")
            caption.grid(row=1, column=index, sticky="w")
            self._figures.append((value, caption))

    def _build_lower_panels(self) -> None:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=18)
        row.grid_columnconfigure(0, weight=5, uniform="lower")
        row.grid_columnconfigure(1, weight=2, uniform="lower")

        preview = Panel(row, "Aperçu du catalogue")
        preview.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self._preview = DataTable(preview, _COLUMNS, scrollable=False)
        self._preview.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 10))

        quick = Panel(row, "Actions rapides")
        quick.grid(row=0, column=1, sticky="nsew")
        buttons = ctk.CTkFrame(quick, fg_color="transparent")
        buttons.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        for label, handler in (
            ("Emprunter un livre", lambda: self.on_lend()),
            ("Retourner un livre", lambda: self.on_return()),
            ("Ajouter un utilisateur", lambda: self.on_add_member()),
            ("Enregistrer les données", lambda: self.on_save()),
        ):
            make_button(buttons, label, handler, anchor="w").pack(fill="x", pady=4)

        search = Panel(self, "Trouver un livre")
        search.grid(row=3, column=0, sticky="ew", padx=theme.PAGE_PADDING, pady=(0, 28))
        self.search_bar = SearchBar(search, BOOK_SEARCH_CRITERIA, lambda: self.on_search())
        self.search_bar.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 14))
        self._results = DataTable(search, _COLUMNS, scrollable=False)
        self._results_visible = False

    def show_figures(self, figures: Sequence[tuple[int, str]]) -> None:
        for (value_label, caption_label), (value, caption) in zip(self._figures, figures):
            value_label.configure(text=str(value))
            caption_label.configure(text=caption)

    def show_shelf(self, spines: Sequence[Spine]) -> None:
        self._shelf.show(spines)

    def show_preview(self, rows: Sequence[Sequence], empty_text: str) -> None:
        self._preview.set_rows(rows, empty_text)

    def show_results(self, rows: Sequence[Sequence], empty_text: str) -> None:
        if not self._results_visible:
            self._results.grid(row=2, column=0, sticky="ew", padx=2, pady=(0, 10))
            self._results_visible = True
        self._results.set_rows(rows, empty_text)

    def hide_results(self) -> None:
        self._results.grid_remove()
        self._results_visible = False
