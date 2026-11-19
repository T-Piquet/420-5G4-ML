"""Fenêtre principale de la bibliothèque.

La vue ne contient aucune logique métier : elle expose des méthodes de mise à
jour et transmet les actions de l'utilisateur au contrôleur.
"""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from app import config
from app.views.book_table import BookTable
from app.views.dialogs import AddBookDialog, BorrowDialog
from app.views.view_models import BookRow, UserRow


class MainWindow(ctk.CTk):
    """Fenêtre principale : sidebar, recherche, tableau et actions."""

    def __init__(self) -> None:
        super().__init__()

        self._search_callback: Callable[[str], None] | None = None
        self._select_callback: Callable[[str], None] | None = None
        self._navigation_callback: Callable[[str], None] | None = None
        self._add_callback: Callable[[], None] | None = None
        self._borrow_callback: Callable[[], None] | None = None
        self._delete_callback: Callable[[], None] | None = None

        self._books_subtitle = ""
        self._active_section = "Livres"

        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=config.COLOR_BACKGROUND)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self.set_section("Livres")

    # Construction de l'interface

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self,
            width=config.SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=config.COLOR_SURFACE,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 26))
        brand.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            brand,
            text="B",
            width=36,
            height=36,
            corner_radius=10,
            fg_color=config.COLOR_ACCENT,
            text_color=config.COLOR_SURFACE,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 10))

        ctk.CTkLabel(
            brand,
            text=config.APP_NAME,
            anchor="w",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=config.COLOR_TEXT,
        ).grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            brand,
            text=config.APP_SUBTITLE,
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=1, column=1, sticky="ew")

        navigation = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        navigation.grid(row=1, column=0, sticky="ew", padx=12)
        navigation.grid_columnconfigure(0, weight=1)

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for row, section in enumerate(config.NAVIGATION_SECTIONS):
            button = ctk.CTkButton(
                navigation,
                text=section,
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=config.COLOR_TEXT_MUTED,
                hover_color=config.COLOR_ACCENT_SOFT,
                font=ctk.CTkFont(size=13),
                command=lambda name=section: self._on_nav_click(name),
            )
            button.grid(row=row, column=0, sticky="ew", pady=2)
            self._nav_buttons[section] = button

        profile = ctk.CTkFrame(
            self.sidebar,
            fg_color=config.COLOR_BACKGROUND,
            corner_radius=10,
        )
        profile.grid(row=3, column=0, sticky="ew", padx=12, pady=16)
        profile.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            profile,
            text="A",
            width=32,
            height=32,
            corner_radius=16,
            fg_color=config.COLOR_ACCENT_SOFT,
            text_color=config.COLOR_ACCENT,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)

        ctk.CTkLabel(
            profile,
            text="Profil",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=config.COLOR_TEXT,
        ).grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            profile,
            text="Administrateur",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=1, column=1, sticky="ew")

    def _build_content(self) -> None:
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=config.CONTENT_PADDING,
            pady=24,
        )
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)

        self.section_title = ctk.CTkLabel(
            header,
            text="Livres",
            anchor="w",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=config.COLOR_TEXT,
        )
        self.section_title.grid(row=0, column=0, sticky="w")

        self.section_subtitle = ctk.CTkLabel(
            header,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=config.COLOR_TEXT_MUTED,
        )
        self.section_subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.books_body = ctk.CTkFrame(self.main, fg_color="transparent")
        self.books_body.grid(row=1, column=0, sticky="nsew")
        self.books_body.grid_columnconfigure(0, weight=1)
        self.books_body.grid_rowconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.books_body,
            placeholder_text=config.SEARCH_PLACEHOLDER,
            height=42,
            corner_radius=10,
            border_width=1,
            border_color=config.COLOR_BORDER,
            fg_color=config.COLOR_SURFACE,
            text_color=config.COLOR_TEXT,
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        self.book_table = BookTable(
            self.books_body,
            on_select=self._on_row_selected,
        )
        self.book_table.grid(row=1, column=0, sticky="nsew")

        footer = ctk.CTkFrame(self.books_body, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        footer.grid_columnconfigure(0, weight=1)

        self.info_label = ctk.CTkLabel(
            footer,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        )
        self.info_label.grid(row=0, column=0, sticky="w")

        self.status_label = ctk.CTkLabel(
            footer,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        buttons = ctk.CTkFrame(footer, fg_color="transparent")
        buttons.grid(row=0, column=1, rowspan=2, sticky="e")

        self.delete_button = ctk.CTkButton(
            buttons,
            text="Supprimer",
            width=110,
            height=38,
            state="disabled",
            fg_color="transparent",
            border_width=1,
            border_color=config.COLOR_DANGER,
            text_color=config.COLOR_DANGER,
            text_color_disabled=config.COLOR_TEXT_DISABLED,
            hover_color=config.COLOR_DANGER_SOFT,
            font=ctk.CTkFont(size=13),
            command=self._on_delete_click,
        )
        self.delete_button.grid(row=0, column=0, padx=(0, 8))

        self.borrow_button = ctk.CTkButton(
            buttons,
            text="Emprunter",
            width=120,
            height=38,
            state="disabled",
            fg_color=config.COLOR_SURFACE,
            border_width=1,
            border_color=config.COLOR_BORDER,
            text_color=config.COLOR_TEXT,
            text_color_disabled=config.COLOR_TEXT_DISABLED,
            hover_color=config.COLOR_ACCENT_SOFT,
            font=ctk.CTkFont(size=13),
            command=self._on_borrow_click,
        )
        self.borrow_button.grid(row=0, column=1, padx=(0, 8))

        self.add_button = ctk.CTkButton(
            buttons,
            text="Ajouter",
            width=120,
            height=38,
            fg_color=config.COLOR_ACCENT,
            hover_color=config.COLOR_ACCENT_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_add_click,
        )
        self.add_button.grid(row=0, column=2)

        self.placeholder_body = ctk.CTkFrame(
            self.main,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        self.placeholder_body.grid(row=1, column=0, sticky="nsew")
        self.placeholder_label = ctk.CTkLabel(
            self.placeholder_body,
            text="",
            justify="center",
            wraplength=420,
            font=ctk.CTkFont(size=14),
            text_color=config.COLOR_TEXT_MUTED,
        )
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        self.placeholder_body.grid_remove()

    # Callbacks fournis par le contrôleur

    def set_search_callback(self, callback: Callable[[str], None]) -> None:
        self._search_callback = callback

    def set_select_callback(self, callback: Callable[[str], None]) -> None:
        self._select_callback = callback

    def set_navigation_callback(
        self, callback: Callable[[str], None]
    ) -> None:
        self._navigation_callback = callback

    def set_add_callback(self, callback: Callable[[], None]) -> None:
        self._add_callback = callback

    def set_borrow_callback(self, callback: Callable[[], None]) -> None:
        self._borrow_callback = callback

    def set_delete_callback(self, callback: Callable[[], None]) -> None:
        self._delete_callback = callback

    # Mise à jour de l'affichage

    def set_books(self, rows: list[BookRow]) -> None:
        self.book_table.set_rows(rows)

    def set_selected(self, isbn: str | None) -> None:
        self.book_table.set_selected(isbn)

    def set_actions(
        self,
        *,
        can_delete: bool,
        can_borrow: bool,
        borrow_label: str,
    ) -> None:
        self.delete_button.configure(
            state="normal" if can_delete else "disabled"
        )
        self.borrow_button.configure(
            state="normal" if can_borrow else "disabled",
            text=borrow_label,
        )

    def set_footer_info(self, text: str) -> None:
        self.info_label.configure(text=text)

    def set_status(self, message: str, level: str = "info") -> None:
        colors = {
            "success": config.COLOR_SUCCESS,
            "error": config.COLOR_DANGER,
            "info": config.COLOR_TEXT_MUTED,
        }
        self.status_label.configure(
            text=message,
            text_color=colors.get(level, config.COLOR_TEXT_MUTED),
        )

    def set_section_subtitle(self, text: str) -> None:
        self._books_subtitle = text
        if self._active_section == "Livres":
            self.section_subtitle.configure(text=text)

    def set_section(self, section: str) -> None:
        self._active_section = section
        for name, button in self._nav_buttons.items():
            if name == section:
                button.configure(
                    fg_color=config.COLOR_ACCENT_SOFT,
                    text_color=config.COLOR_ACCENT,
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=config.COLOR_TEXT_MUTED,
                )

        self.section_title.configure(text=section)
        if section == "Livres":
            self.section_subtitle.configure(text=self._books_subtitle)
            self.placeholder_body.grid_remove()
            self.books_body.grid()
        else:
            self.section_subtitle.configure(text="Section à venir")
            self.placeholder_label.configure(
                text=f"La section « {section} » sera disponible prochainement."
            )
            self.books_body.grid_remove()
            self.placeholder_body.grid()

    def clear_search(self) -> None:
        self.search_entry.delete(0, "end")
        # CTk 5.2 ne réaffiche pas le placeholder tout seul hors focus.
        self.search_entry.configure(placeholder_text=config.SEARCH_PLACEHOLDER)

    # Dialogues

    def open_add_dialog(
        self, on_submit: Callable[[str, str, str], str | None]
    ) -> None:
        AddBookDialog(self, on_submit)

    def open_borrow_dialog(
        self,
        book_title: str,
        users: list[UserRow],
        on_submit: Callable[[str], str | None],
    ) -> None:
        BorrowDialog(self, book_title, users, on_submit)

    def confirm_delete(self, title: str) -> bool:
        return messagebox.askyesno(
            "Supprimer un livre",
            f"Supprimer « {title} » de la bibliothèque ?",
            parent=self,
        )

    # Événements internes

    def _on_search_key(self, _event) -> None:
        if self._search_callback is not None:
            self._search_callback(self.search_entry.get())

    def _on_row_selected(self, isbn: str) -> None:
        self.book_table.set_selected(isbn)
        if self._select_callback is not None:
            self._select_callback(isbn)

    def _on_nav_click(self, section: str) -> None:
        self.set_section(section)
        if self._navigation_callback is not None:
            self._navigation_callback(section)

    def _on_add_click(self) -> None:
        if self._add_callback is not None:
            self._add_callback()

    def _on_borrow_click(self) -> None:
        if self._borrow_callback is not None:
            self._borrow_callback()

    def _on_delete_click(self) -> None:
        if self._delete_callback is not None:
            self._delete_callback()
