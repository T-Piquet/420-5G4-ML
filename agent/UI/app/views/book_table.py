"""Tableau scrollable des livres."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from app import config
from app.views.view_models import BookRow

_COLUMN_WEIGHTS = (4, 3, 2, 2)
_COLUMN_TITLES = ("Titre", "Auteur", "ISBN", "Statut")


def shorten(text: str, limit: int) -> str:
    """Tronque un texte trop long pour garder des colonnes stables."""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


class BookTable(ctk.CTkFrame):
    """Carte blanche contenant l'en-tête et les lignes du tableau."""

    def __init__(
        self,
        master,
        on_select: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(
            master,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        self._on_select = on_select
        self._selected_isbn: str | None = None
        self._rows: dict[str, tuple[ctk.CTkFrame, str]] = {}

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
            frame.grid_columnconfigure(column, weight=weight, uniform="book")

    def set_rows(self, rows: list[BookRow]) -> None:
        """Reconstruit entièrement le tableau."""
        for child in self._body.winfo_children():
            child.destroy()
        self._rows.clear()
        self._selected_isbn = None

        if not rows:
            ctk.CTkLabel(
                self._body,
                text="Aucun livre à afficher.",
                font=ctk.CTkFont(size=13),
                text_color=config.COLOR_TEXT_MUTED,
            ).grid(row=0, column=0, pady=48)
            return

        for index, row in enumerate(rows):
            self._add_row(index, row)

    def set_selected(self, isbn: str | None) -> None:
        """Met en évidence la ligne sélectionnée."""
        self._selected_isbn = isbn
        for key, (frame, base_color) in self._rows.items():
            frame.configure(
                fg_color=(
                    config.COLOR_ACCENT_SOFT if key == isbn else base_color
                )
            )

    def _add_row(self, index: int, row: BookRow) -> None:
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

        title = ctk.CTkLabel(
            frame,
            text=shorten(row.title, 44),
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=config.COLOR_TEXT,
        )
        title.grid(row=0, column=0, sticky="ew", padx=(12, 8))

        author = ctk.CTkLabel(
            frame,
            text=shorten(row.author, 28),
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=config.COLOR_TEXT_MUTED,
        )
        author.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        isbn = ctk.CTkLabel(
            frame,
            text=row.isbn,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        )
        isbn.grid(row=0, column=2, sticky="ew", padx=(0, 8))

        status = ctk.CTkLabel(
            frame,
            text=row.status_label,
            width=96,
            height=24,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=(
                config.COLOR_SUCCESS_SOFT
                if row.available
                else config.COLOR_WARNING_SOFT
            ),
            text_color=(
                config.COLOR_SUCCESS if row.available else config.COLOR_WARNING
            ),
        )
        status.grid(row=0, column=3, sticky="w", padx=(0, 12))

        for widget in (frame, title, author, isbn, status):
            widget.bind(
                "<Button-1>",
                lambda _event, isbn=row.isbn: self._handle_click(isbn),
            )
            widget.bind(
                "<Enter>",
                lambda _event, isbn=row.isbn: self._handle_enter(isbn),
            )
            widget.bind(
                "<Leave>",
                lambda _event, isbn=row.isbn: self._handle_leave(isbn),
            )

        self._rows[row.isbn] = (frame, base_color)

    def _handle_click(self, isbn: str) -> None:
        self.set_selected(isbn)
        if self._on_select is not None:
            self._on_select(isbn)

    def _handle_enter(self, isbn: str) -> None:
        entry = self._rows.get(isbn)
        if entry is not None and isbn != self._selected_isbn:
            entry[0].configure(fg_color=config.COLOR_ROW_HOVER)

    def _handle_leave(self, isbn: str) -> None:
        entry = self._rows.get(isbn)
        if entry is not None and isbn != self._selected_isbn:
            entry[0].configure(fg_color=entry[1])
