"""Main application window shell."""

from typing import Dict
import customtkinter as ctk

from bibliotheque_api import BibliothequeAPI
from theme import COLORS
from ui.nav_bar import NavBar
from ui.pages.Stats import StatsPage
from ui.pages.base import BasePage
from ui.pages.books import BooksPage
from ui.pages.settings import SettingsPage
from ui.pages.users import UsersPage


class AppShell(ctk.CTk):
    """Main window hosting the sidebar navigation and page container."""

    def __init__(self, api: BibliothequeAPI) -> None:
        super().__init__()
        self.title("Bibliothèque")
        self.geometry("1040x640")
        self.minsize(860, 520)
        self.configure(fg_color=COLORS["bg_main"])

        self.api = api
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        nav_items = (
            ("books", "Livre/catalogue"),
            ("users", "Membre/utilisateur"),
            ("loans", "Prêt & retours"),
            ("stats", "Statistiques"),
        )
        self.nav_bar = NavBar(self, items=nav_items, on_select=self.show_page)
        self.nav_bar.grid(row=0, column=0, sticky="nsw")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, padx=28, pady=24, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages: Dict[str, BasePage] = {
            "books": BooksPage(self.content, self.api),
            "users": UsersPage(self.content, self.api),
            "loans": SettingsPage(self.content, self.api),
            "stats": StatsPage(self.content, self.api),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("books")

    def show_page(self, key: str) -> None:
        page = self.pages[key]
        page.tkraise()
        page.on_show()
        self.nav_bar.set_active(key)

    def _on_close(self) -> None:
        self.api.save()
        self.destroy()
