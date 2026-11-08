"""Fenêtre principale : barre latérale, barre d'état et pages."""
from collections.abc import Callable

import customtkinter as ctk

from gui.views import theme
from gui.views.pages.catalog import CatalogPage
from gui.views.pages.dashboard import DashboardPage
from gui.views.pages.data import DataPage
from gui.views.pages.loans import LoansPage
from gui.views.pages.members import MembersPage
from gui.views.sidebar import Sidebar
from gui.views.widgets import Toast, make_button, make_label


def _noop() -> None:
    pass


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=theme.BACKGROUND)
        self.title("Bibliothèque")
        self.geometry("1280x820")
        self.minsize(1100, 640)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.on_navigate: Callable[[str], None] = lambda _page: None
        self.on_save: Callable[[], None] = _noop
        self.on_close: Callable[[], None] = _noop
        self.on_find: Callable[[], None] = _noop

        self.sidebar = Sidebar(self, lambda page: self.on_navigate(page))
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        ctk.CTkFrame(self, width=1, fg_color=theme.LINE, corner_radius=0).grid(
            row=0, column=0, rowspan=2, sticky="nse"
        )
        self._build_top_bar()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=1, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        self.dashboard = DashboardPage(container)
        self.catalog = CatalogPage(container)
        self.members = MembersPage(container)
        self.loans = LoansPage(container)
        self.data = DataPage(container)
        self._pages = {
            "dashboard": self.dashboard,
            "catalog": self.catalog,
            "members": self.members,
            "loans": self.loans,
            "data": self.data,
        }
        for page in self._pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()

        self._toast = Toast(self)
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_close())
        self.bind("<Control-s>", lambda _event: self.on_save())
        self.bind("<Control-k>", lambda _event: self.on_find())

    def _build_top_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=1, sticky="ew", padx=theme.PAGE_PADDING, pady=(18, 0))
        bar.grid_columnconfigure(0, weight=1)
        self._save_state = make_label(bar, "", "strong", theme.MUTED)
        self._save_state.grid(row=0, column=1, padx=(0, 12))
        self._save_button = make_button(bar, "Enregistrer", lambda: self.on_save(), "primary")
        self._save_button.grid(row=0, column=2)

    def show_page(self, key: str) -> None:
        for page_key, page in self._pages.items():
            if page_key == key:
                page.grid()
            else:
                page.grid_remove()
        self.sidebar.set_active(key)

    def set_save_state(self, has_unsaved_changes: bool) -> None:
        self._save_state.configure(
            text="Modifications non enregistrées" if has_unsaved_changes else "Tout est enregistré",
            text_color=theme.OCHRE_TEXT if has_unsaved_changes else theme.GREEN_TEXT,
        )
        self._save_button.configure(
            state="normal" if has_unsaved_changes else "disabled",
            fg_color=theme.GREEN if has_unsaved_changes else theme.LINE,
        )

    def toast(self, message: str, is_error: bool = False) -> None:
        self._toast.show(message, is_error)
