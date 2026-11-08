"""Barre latérale de navigation."""
from collections.abc import Callable

import customtkinter as ctk

from gui.views import theme
from gui.views.widgets import make_label

PAGES = (
    ("dashboard", "Accueil"),
    ("catalog", "Catalogue"),
    ("members", "Utilisateurs"),
    ("loans", "Emprunts"),
    ("data", "Données"),
)


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate: Callable[[str], None]) -> None:
        super().__init__(master, width=theme.SIDEBAR_WIDTH, corner_radius=0, fg_color=theme.SURFACE)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=20, pady=(26, 24))
        make_label(
            brand, "B.", "strong", theme.SURFACE, fg_color=theme.GREEN, corner_radius=10,
            width=38, height=38,
        ).pack(side="left", padx=(0, 10))
        make_label(brand, "Bibliothèque", "brand", theme.INK).pack(side="left")

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=12)
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._badges: dict[str, ctk.CTkLabel] = {}
        for key, label in PAGES:
            button = ctk.CTkButton(
                nav, text=label, anchor="w", height=40, corner_radius=theme.RADIUS_SMALL,
                fg_color="transparent", hover_color=theme.SURFACE_ALT, text_color=theme.TEXT,
                font=theme.font("button"), command=lambda page=key: on_navigate(page),
            )
            button.pack(fill="x", pady=2)
            self._buttons[key] = button

        for key in ("catalog", "members", "loans"):
            badge = make_label(
                self._buttons[key], "0", "button_small", theme.MUTED, fg_color=theme.SURFACE_ALT,
                corner_radius=6, width=30, height=22,
            )
            badge.place(relx=1.0, rely=0.5, x=-8, anchor="e")
            badge.bind("<Button-1>", lambda _event, page=key: on_navigate(page))
            self._badges[key] = badge

        self._location = make_label(
            self, "", "small", theme.MUTED, anchor="w", justify="left",
            wraplength=theme.SIDEBAR_WIDTH - 44,
        )
        self._location.grid(row=3, column=0, sticky="ew", padx=22, pady=18)

    def set_active(self, page: str) -> None:
        for key, button in self._buttons.items():
            active = key == page
            button.configure(
                fg_color=theme.GREEN_PALE if active else "transparent",
                text_color=theme.GREEN_DARK if active else theme.TEXT,
            )

    def set_counts(self, counts: dict[str, int]) -> None:
        for key, value in counts.items():
            self._badges[key].configure(text=str(value))

    def set_location(self, text: str) -> None:
        self._location.configure(text=text)
