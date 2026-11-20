"""Tableau scrollable des utilisateurs."""

from __future__ import annotations

import customtkinter as ctk

from app import config
from app.views.book_table import shorten
from app.views.view_models import UserRow

_COLUMN_WEIGHTS = (3, 2, 2, 4)
_COLUMN_TITLES = ("Nom", "Identifiant", "Emprunts", "Livres empruntés")


class UserTable(ctk.CTkFrame):
    """Carte blanche contenant l'en-tête et les lignes des utilisateurs."""

    def __init__(self, master) -> None:
        super().__init__(
            master,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        self._rows: list[tuple[ctk.CTkFrame, str]] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=(14, 24), pady=(14, 8))
        self._configure_columns(header)
        for column, title in enumerate(_COLUMN_TITLES):
            ctk.CTkLabel(
                header,
                text=title.upper(),
                anchor="w",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=config.COLOR_TEXT_MUTED,
            ).grid(
                row=0,
                column=column,
                sticky="w",
                padx=(12 if column == 0 else 0, 12),
            )

        separator = ctk.CTkFrame(self, height=1, fg_color=config.COLOR_BORDER)
        separator.grid(row=1, column=0, sticky="ew", pady=(0, 4))

        self._body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=config.COLOR_BORDER,
            scrollbar_button_hover_color=config.COLOR_TEXT_DISABLED,
        )
        self._body.grid(row=2, column=0, sticky="nsew", padx=(10, 4), pady=(2, 10))
        self._body.grid_columnconfigure(0, weight=1)

    @staticmethod
    def _configure_columns(frame) -> None:
        for column, weight in enumerate(_COLUMN_WEIGHTS):
            frame.grid_columnconfigure(column, weight=weight, uniform="user")

    def set_rows(self, rows: list[UserRow]) -> None:
        """Reconstruit entièrement le tableau."""
        for child in self._body.winfo_children():
            child.destroy()
        self._rows.clear()

        if not rows:
            ctk.CTkLabel(
                self._body,
                text="Aucun utilisateur à afficher.",
                font=ctk.CTkFont(size=13),
                text_color=config.COLOR_TEXT_MUTED,
            ).grid(row=0, column=0, pady=48)
            return

        for index, row in enumerate(rows):
            self._add_row(index, row)

    def _add_row(self, index: int, row: UserRow) -> None:
        base_color = (
            config.COLOR_SURFACE if index % 2 == 0 else config.COLOR_ROW_ALT
        )
        frame = ctk.CTkFrame(
            self._body,
            fg_color=base_color,
            corner_radius=8,
            height=config.ROW_HEIGHT,
        )
        frame.grid(row=index, column=0, sticky="ew", padx=4, pady=2)
        frame.grid_propagate(False)
        self._configure_columns(frame)

        name = ctk.CTkLabel(
            frame,
            text=shorten(row.name, 32),
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=config.COLOR_TEXT,
        )
        name.grid(row=0, column=0, sticky="ew", padx=(12, 8))

        user_id = ctk.CTkLabel(
            frame,
            text=row.user_id,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        )
        user_id.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        borrowed = ctk.CTkLabel(
            frame,
            text="Aucun" if row.borrowed_count == 0 else f"{row.borrowed_count}",
            width=72,
            height=24,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=(
                config.COLOR_ROW_ALT
                if row.borrowed_count == 0
                else config.COLOR_ACCENT_SOFT
            ),
            text_color=(
                config.COLOR_TEXT_MUTED
                if row.borrowed_count == 0
                else config.COLOR_ACCENT
            ),
        )
        borrowed.grid(row=0, column=2, sticky="w", padx=(0, 8))

        titles = ctk.CTkLabel(
            frame,
            text=shorten(row.borrowed_titles, 52) if row.borrowed_titles else "—",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        )
        titles.grid(row=0, column=3, sticky="ew", padx=(0, 12))

        for widget in (frame, name, user_id, borrowed, titles):
            widget.bind(
                "<Enter>",
                lambda _event, target=frame: target.configure(
                    fg_color=config.COLOR_ROW_HOVER
                ),
            )
            widget.bind(
                "<Leave>",
                lambda _event, target=frame, color=base_color: target.configure(
                    fg_color=color
                ),
            )

        self._rows.append((frame, base_color))
