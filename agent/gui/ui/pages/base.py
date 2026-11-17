"""Base page class for all Bibliothèque GUI pages."""

import customtkinter as ctk

from bibliotheque_api import BibliothequeAPI
from theme import COLORS, RADIUS


class BasePage(ctk.CTkFrame):
    """Shared container card for pages."""

    def __init__(self, master, api: BibliothequeAPI) -> None:
        super().__init__(
            master,
            corner_radius=RADIUS["card"],
            fg_color=COLORS["bg_card"],
        )
        self.api = api
        self.grid_columnconfigure(0, weight=1)

    def on_show(self) -> None:
        """Called when the page becomes visible."""
        self.refresh()

    def refresh(self) -> None:
        """Reload page contents from the API."""
        pass
