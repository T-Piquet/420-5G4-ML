"""Fenêtres modales d'ajout et d'emprunt."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk

from app import config
from app.views.view_models import UserRow

SubmitHandler = Callable[[str, str, str], str | None]
UserSubmitHandler = Callable[[str, str], str | None]
BorrowHandler = Callable[[str], str | None]


def _center(
    window: ctk.CTkToplevel,
    parent,
    width: int,
    height: int,
) -> None:
    parent.update_idletasks()
    x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
    y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def _grab(window: ctk.CTkToplevel) -> None:
    try:
        window.grab_set()
    except tk.TclError:
        pass


class AddBookDialog(ctk.CTkToplevel):
    """Modale de création d'un livre."""

    def __init__(self, parent, on_submit: SubmitHandler) -> None:
        super().__init__(parent)
        self._on_submit = on_submit

        self.title("Ajouter un livre")
        self.configure(fg_color=config.COLOR_BACKGROUND)
        self.resizable(False, False)
        self.transient(parent)

        card = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Ajouter un livre",
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=config.COLOR_TEXT,
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 12))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.grid(row=1, column=0, sticky="ew", padx=20)
        fields.grid_columnconfigure(0, weight=1)

        self.title_entry = self._add_field(fields, 0, "Titre")
        self.author_entry = self._add_field(fields, 2, "Auteur")
        self.isbn_entry = self._add_field(fields, 4, "ISBN")

        self.error_label = ctk.CTkLabel(
            card,
            text="",
            anchor="w",
            justify="left",
            wraplength=340,
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_DANGER,
        )
        self.error_label.grid(row=2, column=0, sticky="ew", padx=20, pady=(4, 8))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="e", padx=20, pady=(0, 18))

        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=100,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=config.COLOR_BORDER,
            text_color=config.COLOR_TEXT_MUTED,
            hover_color=config.COLOR_ROW_HOVER,
            font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            buttons,
            text="Ajouter",
            width=110,
            height=36,
            fg_color=config.COLOR_ACCENT,
            hover_color=config.COLOR_ACCENT_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._submit,
        ).grid(row=0, column=1)

        for entry in (self.title_entry, self.author_entry, self.isbn_entry):
            entry.bind("<Return>", lambda _event: self._submit())

        _center(self, parent, 420, 430)
        self.after(80, lambda: _grab(self))
        self.after(140, self._focus_title)

    @staticmethod
    def _add_field(parent, row: int, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            parent,
            text=label,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=row, column=0, sticky="ew", pady=(8, 4))

        entry = ctk.CTkEntry(
            parent,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=config.COLOR_BORDER,
            fg_color=config.COLOR_SURFACE,
            text_color=config.COLOR_TEXT,
            font=ctk.CTkFont(size=13),
        )
        entry.grid(row=row + 1, column=0, sticky="ew")
        return entry

    def _focus_title(self) -> None:
        try:
            self.title_entry.focus_set()
        except tk.TclError:
            pass

    def _show_error(self, message: str) -> None:
        self.error_label.configure(text=message)

    def _submit(self) -> None:
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()

        if not title or not author or not isbn:
            self._show_error("Tous les champs sont obligatoires.")
            return

        error = self._on_submit(title, author, isbn)
        if error:
            self._show_error(error)
            return

        self.destroy()


class AddUserDialog(ctk.CTkToplevel):
    """Modale de création d'un utilisateur."""

    def __init__(self, parent, on_submit: UserSubmitHandler) -> None:
        super().__init__(parent)
        self._on_submit = on_submit

        self.title("Ajouter un utilisateur")
        self.configure(fg_color=config.COLOR_BACKGROUND)
        self.resizable(False, False)
        self.transient(parent)

        card = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Ajouter un utilisateur",
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=config.COLOR_TEXT,
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 12))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.grid(row=1, column=0, sticky="ew", padx=20)
        fields.grid_columnconfigure(0, weight=1)

        self.name_entry = self._add_field(fields, 0, "Nom")
        self.user_id_entry = self._add_field(fields, 2, "Identifiant")

        self.error_label = ctk.CTkLabel(
            card,
            text="",
            anchor="w",
            justify="left",
            wraplength=340,
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_DANGER,
        )
        self.error_label.grid(row=2, column=0, sticky="ew", padx=20, pady=(4, 8))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="e", padx=20, pady=(0, 18))

        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=100,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=config.COLOR_BORDER,
            text_color=config.COLOR_TEXT_MUTED,
            hover_color=config.COLOR_ROW_HOVER,
            font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            buttons,
            text="Ajouter",
            width=110,
            height=36,
            fg_color=config.COLOR_ACCENT,
            hover_color=config.COLOR_ACCENT_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._submit,
        ).grid(row=0, column=1)

        for entry in (self.name_entry, self.user_id_entry):
            entry.bind("<Return>", lambda _event: self._submit())

        _center(self, parent, 420, 360)
        self.after(80, lambda: _grab(self))
        self.after(140, self._focus_name)

    @staticmethod
    def _add_field(parent, row: int, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            parent,
            text=label,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=row, column=0, sticky="ew", pady=(8, 4))

        entry = ctk.CTkEntry(
            parent,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=config.COLOR_BORDER,
            fg_color=config.COLOR_SURFACE,
            text_color=config.COLOR_TEXT,
            font=ctk.CTkFont(size=13),
        )
        entry.grid(row=row + 1, column=0, sticky="ew")
        return entry

    def _focus_name(self) -> None:
        try:
            self.name_entry.focus_set()
        except tk.TclError:
            pass

    def _show_error(self, message: str) -> None:
        self.error_label.configure(text=message)

    def _submit(self) -> None:
        name = self.name_entry.get().strip()
        user_id = self.user_id_entry.get().strip()

        if not name or not user_id:
            self._show_error("Tous les champs sont obligatoires.")
            return

        error = self._on_submit(name, user_id)
        if error:
            self._show_error(error)
            return

        self.destroy()


class BorrowDialog(ctk.CTkToplevel):
    """Modale de choix de l'utilisateur qui emprunte un livre."""

    def __init__(
        self,
        parent,
        book_title: str,
        users: list[UserRow],
        on_submit: BorrowHandler,
    ) -> None:
        super().__init__(parent)
        self._on_submit = on_submit
        self._users = users
        self._selected_user_id: str | None = None
        self._user_buttons: dict[str, ctk.CTkButton] = {}

        self.title("Emprunter un livre")
        self.configure(fg_color=config.COLOR_BACKGROUND)
        self.resizable(False, False)
        self.transient(parent)

        card = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=f"Emprunter « {book_title} »",
            anchor="w",
            justify="left",
            wraplength=340,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=config.COLOR_TEXT,
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))

        ctk.CTkLabel(
            card,
            text="Choisissez l'utilisateur :",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

        user_list = ctk.CTkScrollableFrame(
            card,
            height=220,
            fg_color=config.COLOR_BACKGROUND,
            corner_radius=10,
        )
        user_list.grid(row=2, column=0, sticky="ew", padx=20)
        user_list.grid_columnconfigure(0, weight=1)

        if users:
            for index, user in enumerate(users):
                button = ctk.CTkButton(
                    user_list,
                    text=f"{user.name}   ·   {user.user_id}",
                    anchor="w",
                    height=34,
                    corner_radius=6,
                    fg_color="transparent",
                    text_color=config.COLOR_TEXT,
                    hover_color=config.COLOR_ACCENT_SOFT,
                    font=ctk.CTkFont(size=13),
                    command=lambda user_id=user.user_id: self._select(user_id),
                )
                button.grid(row=index, column=0, sticky="ew", padx=4, pady=2)
                self._user_buttons[user.user_id] = button
        else:
            ctk.CTkLabel(
                user_list,
                text="Aucun utilisateur enregistré.",
                font=ctk.CTkFont(size=13),
                text_color=config.COLOR_TEXT_MUTED,
            ).grid(row=0, column=0, pady=40)

        self.error_label = ctk.CTkLabel(
            card,
            text="",
            anchor="w",
            justify="left",
            wraplength=340,
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_DANGER,
        )
        self.error_label.grid(row=3, column=0, sticky="ew", padx=20, pady=(6, 8))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="e", padx=20, pady=(0, 18))

        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=100,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=config.COLOR_BORDER,
            text_color=config.COLOR_TEXT_MUTED,
            hover_color=config.COLOR_ROW_HOVER,
            font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))

        self.submit_button = ctk.CTkButton(
            buttons,
            text="Emprunter",
            width=110,
            height=36,
            fg_color=config.COLOR_ACCENT,
            hover_color=config.COLOR_ACCENT_HOVER,
            text_color_disabled=config.COLOR_TEXT_DISABLED,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled",
            command=self._submit,
        )
        self.submit_button.grid(row=0, column=1)

        _center(self, parent, 420, 500)
        self.after(80, lambda: _grab(self))

    def _select(self, user_id: str) -> None:
        self._selected_user_id = user_id
        for key, button in self._user_buttons.items():
            if key == user_id:
                button.configure(
                    fg_color=config.COLOR_ACCENT_SOFT,
                    text_color=config.COLOR_ACCENT,
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=config.COLOR_TEXT,
                )
        self.submit_button.configure(state="normal")
        self.error_label.configure(text="")

    def _submit(self) -> None:
        if self._selected_user_id is None:
            return

        error = self._on_submit(self._selected_user_id)
        if error:
            self.error_label.configure(text=error)
            return

        self.destroy()
