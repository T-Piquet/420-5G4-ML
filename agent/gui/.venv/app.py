"""Interface graphique CustomTkinter de la bibliothèque personnelle."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from library import Book, Library, LibraryError, User
import theme

PAGE_SIZE = 12
SETTINGS_PATH = Path.home() / ".config" / "bibliotheque" / "settings.json"


def load_appearance_mode() -> str:
    try:
        settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "light"
    mode = settings.get("appearance_mode") if isinstance(settings, dict) else None
    return mode if mode in ("light", "dark") else "light"


def save_appearance_mode(mode: str) -> None:
    if mode not in {"light", "dark"}:
        return
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(
            json.dumps({"appearance_mode": mode}) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def default_data_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "data"
        if (candidate / "books.txt").is_file() and (candidate / "users.txt").is_file():
            return candidate
    return here.parents[2] / "data"


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, label: str, value: str, accent: theme.Color = theme.PRIMARY):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            corner_radius=20,
            border_width=1,
            border_color=theme.BORDER,
        )
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text=label,
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 0))
        ctk.CTkLabel(
            self,
            text=value,
            font=theme.FONT_METRIC,
            text_color=accent,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app: "LibraryApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="Tableau de bord",
            font=theme.FONT_TITLE,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(6, 4))
        ctk.CTkLabel(
            self,
            text="Vue d'ensemble de la collection et des emprunts en cours.",
            font=theme.FONT_SUBTITLE,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 16))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="new")
        for column in range(4):
            cards.grid_columnconfigure(column, weight=1)
        values = [
            ("Livres", str(app.library.total_books()), theme.PRIMARY),
            ("Disponibles", str(app.library.available_count()), theme.SUCCESS),
            ("Empruntés", str(app.library.checked_out_count()), theme.WARNING),
            ("Usagers", str(app.library.total_users()), theme.SECONDARY),
        ]
        for column, (label, value, accent) in enumerate(values):
            card = MetricCard(cards, label, value, accent)
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 8, 0 if column == 3 else 8),
            )

        available = app.library.available_books()
        panel = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=20,
            border_width=1,
            border_color=theme.BORDER,
        )
        panel.grid(row=3, column=0, sticky="nsew", pady=(16, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            panel,
            text=f"Disponibles à l'emprunt · {len(available)}",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 10))

        listing = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color=theme.SECONDARY,
            scrollbar_button_hover_color=theme.PRIMARY,
        )
        listing.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 14))
        listing.grid_columnconfigure(0, weight=1)

        if not available:
            ctk.CTkLabel(
                listing,
                text="Aucun livre disponible pour le moment.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=0, sticky="w", padx=12, pady=16)
        else:
            for row, book in enumerate(available):
                item = ctk.CTkFrame(listing, fg_color=theme.ROW_ALT, corner_radius=14)
                item.grid(row=row, column=0, sticky="ew", pady=4)
                item.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    item,
                    text=book.title,
                    font=theme.FONT_BODY_BOLD,
                    text_color=theme.TEXT,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
                ctk.CTkLabel(
                    item,
                    text=f"{book.author} · {book.isbn}",
                    font=theme.FONT_SMALL,
                    text_color=theme.TEXT_MUTED,
                    anchor="w",
                ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
                ctk.CTkButton(
                    item,
                    text="Emprunter",
                    width=118,
                    height=36,
                    font=theme.FONT_SMALL,
                    fg_color=theme.SECONDARY,
                    hover_color=theme.PRIMARY,
                    command=lambda b=book: app.borrow_book(b),
                ).grid(row=0, column=1, rowspan=2, padx=14, pady=10)


class BooksView(ctk.CTkFrame):
    def __init__(self, master, app: "LibraryApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", pady=(2, 8))
        heading.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            heading,
            text="Livres",
            font=theme.FONT_TITLE,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            heading,
            text=f"{len(app.library.books)} livre(s) dans la bibliothèque",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED,
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        self.books = app.filtered_books()
        total = len(self.books)
        pages = max(1, math.ceil(total / PAGE_SIZE))
        app.page = min(app.page, pages - 1)
        start = app.page * PAGE_SIZE
        page_books = self.books[start : start + PAGE_SIZE]

        header = ctk.CTkFrame(self, fg_color=theme.PRIMARY, corner_radius=16)
        header.grid(row=1, column=0, sticky="ew")
        self._configure_columns(header)
        for column, text in enumerate(("Titre", "Auteur", "ISBN", "Statut", "Actions")):
            ctk.CTkLabel(
                header,
                text=text,
                font=theme.FONT_BODY_BOLD,
                text_color=theme.TEXT_ON_PRIMARY,
                anchor="w",
            ).grid(row=0, column=column, sticky="ew", padx=16, pady=8)

        listing = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        listing.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        listing.grid_columnconfigure(0, weight=1)

        if not page_books:
            ctk.CTkLabel(
                listing,
                text="Aucun livre ne correspond à la recherche.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=0, sticky="w", padx=16, pady=28)
        else:
            for row in range(PAGE_SIZE):
                listing.grid_rowconfigure(row, weight=1, uniform="book_row")
            for row, book in enumerate(page_books):
                self._book_row(listing, row, book)
            for row in range(len(page_books), PAGE_SIZE):
                ctk.CTkFrame(
                    listing,
                    fg_color="transparent",
                    width=1,
                    height=1,
                ).grid(row=row, column=0, sticky="nsew", pady=1)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        footer.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            footer,
            text=f"Page {app.page + 1} / {pages} · {total} résultat(s)",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        previous = ctk.CTkButton(
            footer,
            text="‹",
            width=44,
            height=30,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SECONDARY,
            hover_color=theme.PRIMARY,
            state="normal" if app.page > 0 else "disabled",
            command=lambda: app.change_page(-1),
        )
        previous.grid(row=0, column=1, padx=(0, 8))
        following = ctk.CTkButton(
            footer,
            text="›",
            width=44,
            height=30,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SECONDARY,
            hover_color=theme.PRIMARY,
            state="normal" if app.page < pages - 1 else "disabled",
            command=lambda: app.change_page(1),
        )
        following.grid(row=0, column=2)

    @staticmethod
    def _configure_columns(frame: ctk.CTkFrame) -> None:
        frame.grid_columnconfigure(0, weight=5, uniform="books")
        frame.grid_columnconfigure(1, weight=4, uniform="books")
        frame.grid_columnconfigure(2, weight=3, uniform="books")
        frame.grid_columnconfigure(3, weight=3, uniform="books")
        frame.grid_columnconfigure(4, weight=5, uniform="books")

    def _book_row(self, master: ctk.CTkFrame, row: int, book: Book) -> None:
        background = theme.ROW_ALT if row % 2 == 0 else theme.SURFACE
        item = ctk.CTkFrame(master, fg_color=background, corner_radius=14)
        item.grid(row=row, column=0, sticky="nsew", pady=1)
        self._configure_columns(item)
        item.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            item,
            text=book.title,
            font=theme.FONT_BODY_BOLD,
            text_color=theme.TEXT,
            anchor="w",
            justify="left",
            wraplength=270,
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=4)
        ctk.CTkLabel(
            item,
            text=book.author,
            font=theme.FONT_BODY,
            text_color=theme.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=210,
        ).grid(row=0, column=1, sticky="ew", padx=16, pady=4)
        ctk.CTkLabel(
            item,
            text=book.isbn,
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED,
            anchor="w",
            justify="left",
        ).grid(row=0, column=2, sticky="ew", padx=16, pady=4)

        available = book.available
        ctk.CTkLabel(
            item,
            text=book.status,
            font=theme.FONT_SMALL,
            text_color=theme.SUCCESS if available else theme.WARNING,
            fg_color=theme.SUCCESS_SOFT if available else theme.WARNING_SOFT,
            corner_radius=12,
            padx=12,
            pady=3,
        ).grid(row=0, column=3, sticky="w", padx=16, pady=2)

        actions = ctk.CTkFrame(item, fg_color="transparent")
        actions.grid(row=0, column=4, sticky="w", padx=16)
        if available:
            ctk.CTkButton(
                actions,
                text="Emprunter",
                width=100,
                height=28,
                font=theme.FONT_SMALL,
                fg_color=theme.SECONDARY,
                hover_color=theme.PRIMARY,
                command=lambda b=book: self.app.borrow_book(b),
            ).grid(row=0, column=0, padx=(0, 8))
        else:
            ctk.CTkButton(
                actions,
                text="Retourner",
                width=100,
                height=28,
                font=theme.FONT_SMALL,
                fg_color=theme.ACCENT,
                hover_color=theme.SECONDARY,
                text_color=theme.TEXT,
                command=lambda b=book: self.app.return_book(b),
            ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            actions,
            text="Supprimer",
            width=90,
            height=28,
            font=theme.FONT_SMALL,
            fg_color=theme.DANGER_SOFT,
            hover_color=theme.DANGER,
            text_color=theme.DANGER,
            command=lambda b=book: self.app.delete_book(b),
        ).grid(row=0, column=1)


class UsersView(ctk.CTkFrame):
    def __init__(self, master, app: "LibraryApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", pady=(2, 8))
        heading.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            heading,
            text="Usagers",
            font=theme.FONT_TITLE,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.users = app.library.users
        total = len(self.users)
        pages = max(1, math.ceil(total / PAGE_SIZE))
        app.user_page = min(app.user_page, pages - 1)
        start = app.user_page * PAGE_SIZE
        page_users = self.users[start : start + PAGE_SIZE]

        header = ctk.CTkFrame(self, fg_color=theme.PRIMARY, corner_radius=16)
        header.grid(row=1, column=0, sticky="ew")
        for column, weight in enumerate((4, 3, 5)):
            header.grid_columnconfigure(column, weight=weight, uniform="users")
        for column, text in enumerate(("Nom", "Identifiant", "Livres empruntés")):
            ctk.CTkLabel(
                header,
                text=text,
                font=theme.FONT_BODY_BOLD,
                text_color=theme.TEXT_ON_PRIMARY,
                anchor="w",
            ).grid(row=0, column=column, sticky="ew", padx=16, pady=8)

        listing = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        listing.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        listing.grid_columnconfigure(0, weight=1)

        if not page_users:
            ctk.CTkLabel(
                listing,
                text="Aucun utilisateur enregistré.",
                font=theme.FONT_BODY,
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=0, sticky="w", padx=16, pady=28)
        else:
            for row in range(PAGE_SIZE):
                listing.grid_rowconfigure(row, weight=1, uniform="user_row")
            for row, user in enumerate(page_users):
                background = theme.ROW_ALT if row % 2 == 0 else theme.SURFACE
                item = ctk.CTkFrame(listing, fg_color=background, corner_radius=14)
                item.grid(row=row, column=0, sticky="nsew", pady=1)
                for column, weight in enumerate((4, 3, 5)):
                    item.grid_columnconfigure(column, weight=weight, uniform="users")
                item.grid_rowconfigure(0, weight=1)
                ctk.CTkLabel(
                    item,
                    text=user.name,
                    font=theme.FONT_BODY_BOLD,
                    text_color=theme.TEXT,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=16, pady=4)
                ctk.CTkLabel(
                    item,
                    text=user.user_id,
                    font=theme.FONT_BODY,
                    text_color=theme.TEXT_MUTED,
                    anchor="w",
                ).grid(row=0, column=1, sticky="ew", padx=16, pady=4)
                borrowed = user.borrowed_books
                detail = f"{len(borrowed)} · {', '.join(borrowed)}" if borrowed else "0"
                ctk.CTkLabel(
                    item,
                    text=detail,
                    font=theme.FONT_SMALL,
                    text_color=theme.TEXT_MUTED,
                    anchor="w",
                    justify="left",
                    wraplength=360,
                ).grid(row=0, column=2, sticky="ew", padx=16, pady=4)
            for row in range(len(page_users), PAGE_SIZE):
                ctk.CTkFrame(
                    listing,
                    fg_color="transparent",
                    width=1,
                    height=1,
                ).grid(row=row, column=0, sticky="nsew", pady=1)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        footer.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            footer,
            text=f"Page {app.user_page + 1} / {pages} · {total} résultat(s)",
            font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        previous = ctk.CTkButton(
            footer,
            text="‹",
            width=44,
            height=30,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SECONDARY,
            hover_color=theme.PRIMARY,
            state="normal" if app.user_page > 0 else "disabled",
            command=lambda: app.change_user_page(-1),
        )
        previous.grid(row=0, column=1, padx=(0, 8))
        following = ctk.CTkButton(
            footer,
            text="›",
            width=44,
            height=30,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SECONDARY,
            hover_color=theme.PRIMARY,
            state="normal" if app.user_page < pages - 1 else "disabled",
            command=lambda: app.change_user_page(1),
        )
        following.grid(row=0, column=2)


class StatsView(ctk.CTkFrame):
    def __init__(self, master, app: "LibraryApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Statistiques",
            font=theme.FONT_TITLE,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(6, 4))
        ctk.CTkLabel(
            self,
            text="Indicateurs de disponibilité de la bibliothèque.",
            font=theme.FONT_SUBTITLE,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 16))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=2, column=0, sticky="new")
        for column in range(3):
            cards.grid_columnconfigure(column, weight=1)
        values = [
            ("Livres disponibles", str(app.library.available_count()), theme.SUCCESS),
            ("Livres empruntés", str(app.library.checked_out_count()), theme.WARNING),
            ("Usagers inscrits", str(app.library.total_users()), theme.SECONDARY),
        ]
        for column, (label, value, accent) in enumerate(values):
            card = MetricCard(cards, label, value, accent)
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 8, 0 if column == 2 else 8),
            )

        panel = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=20,
            border_width=1,
            border_color=theme.BORDER,
        )
        panel.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        panel.grid_columnconfigure(0, weight=1)
        total = app.library.total_books()
        ratio = app.library.available_count() / total if total else 0
        ctk.CTkLabel(
            panel,
            text="Taux de disponibilité",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(22, 10))
        bar = ctk.CTkProgressBar(
            panel,
            height=20,
            corner_radius=10,
            fg_color=theme.ACCENT,
            progress_color=theme.SUCCESS,
        )
        bar.grid(row=1, column=0, sticky="ew", padx=22, pady=10)
        bar.set(ratio)
        ctk.CTkLabel(
            panel,
            text=f"{app.library.available_count()} disponible(s) sur {total} livre(s)",
            font=theme.FONT_BODY,
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=22, pady=(10, 22))


class AddBookDialog(ctk.CTkToplevel):
    def __init__(self, master: "LibraryApp"):
        super().__init__(master)
        self.app = master
        self.title("Ajouter un livre")
        self.resizable(False, False)
        self.configure(fg_color=theme.BACKGROUND)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text="Ajouter un livre",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT,
        ).grid(row=0, column=0, padx=28, pady=(24, 14))

        form = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=18)
        form.grid(row=1, column=0, sticky="ew", padx=24)
        form.grid_columnconfigure(1, weight=1)
        self.title_entry = self._field(form, 0, "Titre")
        self.author_entry = self._field(form, 1, "Auteur")
        self.isbn_entry = self._field(form, 2, "ISBN")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="e", padx=24, pady=20)
        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=112,
            height=42,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SURFACE,
            hover_color=theme.ACCENT,
            text_color=theme.TEXT,
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            buttons,
            text="Ajouter",
            width=122,
            height=42,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.PRIMARY,
            hover_color=theme.SECONDARY,
            command=self.submit,
        ).grid(row=0, column=1)

        self.bind("<Return>", lambda _event: self.submit())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.after(60, self._center)

    def _field(self, master: ctk.CTkFrame, row: int, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            master,
            text=label,
            font=theme.FONT_BODY,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=row, column=0, sticky="w", padx=(20, 12), pady=12)
        entry = ctk.CTkEntry(
            master,
            height=42,
            font=theme.FONT_BODY,
            fg_color=theme.ROW_ALT,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=12)
        return entry

    def _center(self) -> None:
        self.update_idletasks()
        x = self.app.winfo_rootx() + (self.app.winfo_width() - self.winfo_width()) // 2
        y = self.app.winfo_rooty() + (self.app.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.title_entry.focus_set()

    def submit(self) -> None:
        try:
            self.app.library.add_book(
                self.title_entry.get(),
                self.author_entry.get(),
                self.isbn_entry.get(),
            )
        except LibraryError as exc:
            messagebox.showerror("Ajout impossible", str(exc), parent=self)
            return
        if not self.app.persist():
            return
        self.app.refresh(navigate="books")
        self.destroy()


class AddUserDialog(ctk.CTkToplevel):
    def __init__(self, master: "LibraryApp"):
        super().__init__(master)
        self.app = master
        self.title("Ajouter un utilisateur")
        self.resizable(False, False)
        self.configure(fg_color=theme.BACKGROUND)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text="Ajouter un utilisateur",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT,
        ).grid(row=0, column=0, padx=28, pady=(24, 14))

        form = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=18)
        form.grid(row=1, column=0, sticky="ew", padx=24)
        form.grid_columnconfigure(1, weight=1)
        self.name_entry = self._field(form, 0, "Nom")
        self.id_entry = self._field(form, 1, "Identifiant")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="e", padx=24, pady=20)
        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=112,
            height=42,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SURFACE,
            hover_color=theme.ACCENT,
            text_color=theme.TEXT,
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            buttons,
            text="Ajouter",
            width=122,
            height=42,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.PRIMARY,
            hover_color=theme.SECONDARY,
            command=self.submit,
        ).grid(row=0, column=1)

        self.bind("<Return>", lambda _event: self.submit())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.after(60, self._center)

    def _field(self, master: ctk.CTkFrame, row: int, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            master,
            text=label,
            font=theme.FONT_BODY,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=row, column=0, sticky="w", padx=(20, 12), pady=12)
        entry = ctk.CTkEntry(
            master,
            height=42,
            font=theme.FONT_BODY,
            fg_color=theme.ROW_ALT,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=12)
        return entry

    def _center(self) -> None:
        self.update_idletasks()
        x = self.app.winfo_rootx() + (self.app.winfo_width() - self.winfo_width()) // 2
        y = self.app.winfo_rooty() + (self.app.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.name_entry.focus_set()

    def submit(self) -> None:
        try:
            self.app.library.add_user(self.name_entry.get(), self.id_entry.get())
        except LibraryError as exc:
            messagebox.showerror("Ajout impossible", str(exc), parent=self)
            return
        if not self.app.persist():
            return
        self.app.refresh(navigate="users")
        self.destroy()


class BorrowDialog(ctk.CTkToplevel):
    def __init__(self, master: "LibraryApp", book: Book):
        super().__init__(master)
        self.app = master
        self.book = book
        self.title("Emprunter un livre")
        self.resizable(False, False)
        self.configure(fg_color=theme.BACKGROUND)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text="Emprunter un livre",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT,
        ).grid(row=0, column=0, padx=28, pady=(24, 8))
        ctk.CTkLabel(
            self,
            text=f"« {book.title} » de {book.author}",
            font=theme.FONT_BODY,
            text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, padx=28, pady=(0, 16))

        panel = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=18)
        panel.grid(row=2, column=0, sticky="ew", padx=24)
        panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            panel,
            text="Choisir l'usager",
            font=theme.FONT_BODY,
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 8))
        self.users = {f"{user.name} ({user.user_id})": user.user_id for user in master.library.users}
        self.combo = ctk.CTkComboBox(
            panel,
            values=list(self.users) or ["Aucun usager"],
            state="readonly",
            height=42,
            font=theme.FONT_BODY,
            dropdown_font=theme.FONT_BODY,
            fg_color=theme.ROW_ALT,
            border_color=theme.BORDER,
            button_color=theme.SECONDARY,
            button_hover_color=theme.PRIMARY,
        )
        self.combo.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 18))
        if self.users:
            self.combo.set(next(iter(self.users)))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="e", padx=24, pady=20)
        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=112,
            height=42,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SURFACE,
            hover_color=theme.ACCENT,
            text_color=theme.TEXT,
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            buttons,
            text="Confirmer",
            width=122,
            height=42,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.PRIMARY,
            hover_color=theme.SECONDARY,
            state="normal" if self.users else "disabled",
            command=self.submit,
        ).grid(row=0, column=1)

        self.bind("<Return>", lambda _event: self.submit())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.after(60, self._center)

    def _center(self) -> None:
        self.update_idletasks()
        x = self.app.winfo_rootx() + (self.app.winfo_width() - self.winfo_width()) // 2
        y = self.app.winfo_rooty() + (self.app.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.combo.focus_set()

    def submit(self) -> None:
        if not self.users:
            self.destroy()
            return
        user_id = self.users.get(self.combo.get())
        if not user_id:
            return
        try:
            self.app.library.check_out_book(self.book.isbn, user_id)
        except LibraryError as exc:
            messagebox.showerror("Emprunt impossible", str(exc), parent=self)
            return
        if not self.app.persist():
            return
        self.app.refresh(navigate="books")
        self.destroy()


def resolve_color(color: theme.Color, mode: str) -> str:
    return color[0] if mode == "light" else color[1]


def color_luminance(color: str) -> float:
    value = color.lstrip("#")
    red, green, blue = (int(value[index : index + 2], 16) for index in (0, 2, 4))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


class SidebarItem(ctk.CTkFrame):
    def __init__(
        self,
        master,
        app: "LibraryApp",
        key: str,
        label: str,
        icon: str,
        command,
        role: str = "nav",
    ):
        super().__init__(master, fg_color=theme.BACKGROUND, corner_radius=14, height=52)
        self.app = app
        self.key = key
        self.icon_kind = icon
        self.command = command
        self.role = role
        self._active = False
        self._hovered = False
        self._expanded = app.sidebar_expanded
        (
            self._normal_fg,
            self._hover_fg,
            self._normal_text,
            self._hover_text,
        ) = self._role_colors()
        self.configure(width=184 if self._expanded else 56)
        self.pack_propagate(False)

        self.icon_canvas = tk.Canvas(
            self,
            width=28,
            height=28,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.icon_canvas.pack(side="left", padx=(14, 10))
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=theme.FONT_BODY_BOLD,
            anchor="w",
            cursor="hand2",
        )
        self.label.pack(side="left")

        for widget in (self, self.icon_canvas, self.label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

        self.set_expanded(self._expanded)
        self.refresh_theme()

    def _role_colors(self) -> tuple[theme.Color, theme.Color, theme.Color, theme.Color]:
        if self.role == "save":
            return theme.SECONDARY, theme.PRIMARY, theme.TEXT_ON_PRIMARY, theme.TEXT_ON_PRIMARY
        if self.role == "backup":
            return theme.SURFACE, theme.ACCENT, theme.TEXT, theme.TEXT
        if self.role == "quit":
            return theme.DANGER_SOFT, theme.DANGER, theme.DANGER, theme.TEXT_ON_PRIMARY
        return theme.BACKGROUND, theme.ACCENT, theme.TEXT, theme.TEXT

    def _on_click(self, _event=None) -> None:
        self.command()

    def _on_enter(self, _event=None) -> None:
        if not self._hovered:
            self._hovered = True
            self.refresh_theme()

    def _on_leave(self, _event=None) -> None:
        x, y = self.winfo_pointerxy()
        left = self.winfo_rootx()
        top = self.winfo_rooty()
        if left <= x < left + self.winfo_width() and top <= y < top + self.winfo_height():
            return
        if self._hovered:
            self._hovered = False
            self.refresh_theme()

    def set_active(self, active: bool) -> None:
        self._active = active
        self.refresh_theme()

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self.configure(width=184 if expanded else 56)
        if expanded:
            self.label.pack(side="left")
            self.icon_canvas.pack_configure(side="left", padx=(14, 10), expand=False)
        else:
            self.label.pack_forget()
            self.icon_canvas.pack_configure(side="left", padx=0, expand=True)

    def set_label(self, text: str) -> None:
        self.label.configure(text=text)

    def set_icon(self, icon_kind: str) -> None:
        self.icon_kind = icon_kind
        self.refresh_theme()

    def refresh_theme(self) -> None:
        if self._active:
            background = theme.SECONDARY
            text_color = theme.TEXT_ON_PRIMARY
        elif self._hovered:
            background = self._hover_fg
            text_color = self._hover_text
        else:
            background = self._normal_fg
            text_color = self._normal_text

        mode = self.app.appearance_mode
        self.configure(fg_color=background)
        self.label.configure(text_color=text_color)
        self.icon_canvas.configure(bg=resolve_color(background, mode))
        self._draw_icon(resolve_color(text_color, mode))

    def _draw_icon(self, color: str) -> None:
        canvas = self.icon_canvas
        canvas.delete("all")
        if self.icon_kind == "dashboard":
            for x in (4, 15):
                for y in (4, 15):
                    canvas.create_rectangle(x, y, x + 9, y + 9, outline=color, width=2)
        elif self.icon_kind == "books":
            canvas.create_rectangle(5, 3, 23, 25, outline=color, width=2)
            canvas.create_line(9, 3, 9, 25, fill=color, width=2)
            for y in (8, 12, 16):
                canvas.create_line(12, y, 20, y, fill=color, width=2)
        elif self.icon_kind == "users":
            def bust(x0: float, top: float, x1: float, bottom: float, cap: float) -> None:
                canvas.create_oval(x0, top, x1, top + cap, fill=color, outline=color)
                canvas.create_rectangle(
                    x0, top + cap / 2, x1, bottom, fill=color, outline=color
                )

            canvas.create_oval(2, 7, 9, 14, fill=color, outline=color)
            canvas.create_oval(19, 7, 26, 14, fill=color, outline=color)
            canvas.create_oval(9, 2, 19, 12, fill=color, outline=color)
            bust(-5, 15, 6, 25.8, 9)
            bust(22, 15, 33, 25.8, 9)
            bust(7.5, 13, 20.5, 25.8, 10)
        elif self.icon_kind == "stats":
            canvas.create_rectangle(5, 15, 9, 24, fill=color, outline=color)
            canvas.create_rectangle(12, 8, 16, 24, fill=color, outline=color)
            canvas.create_rectangle(19, 12, 23, 24, fill=color, outline=color)
            canvas.create_line(3, 25, 25, 25, fill=color, width=2)
        elif self.icon_kind == "toggle_collapse":
            for right in (17, 24):
                canvas.create_line(
                    right, 7, right - 7, 14, right, 21,
                    fill=color, width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND,
                )
        elif self.icon_kind == "toggle_expand":
            for left in (4, 11):
                canvas.create_line(
                    left, 7, left + 7, 14, left, 21,
                    fill=color, width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND,
                )
        elif self.icon_kind == "save":
            canvas.create_rectangle(5, 4, 23, 24, outline=color, width=2)
            canvas.create_rectangle(9, 4, 19, 10, outline=color, width=2)
            canvas.create_rectangle(9, 15, 19, 24, outline=color, width=2)
        elif self.icon_kind == "backup":
            canvas.create_rectangle(9, 4, 24, 19, outline=color, width=2)
            canvas.create_line(5, 8, 5, 24, 20, 24, 20, 19, fill=color, width=2)
        elif self.icon_kind == "quit":
            canvas.create_arc(
                5, 4, 23, 22, start=30, extent=300, style=tk.ARC, outline=color, width=2
            )
            canvas.create_line(14, 3, 14, 14, fill=color, width=2)


class LibraryApp(ctk.CTk):
    def __init__(self, data_dir: Path, appearance_mode: str | None = None):
        mode = appearance_mode if appearance_mode in {"light", "dark"} else load_appearance_mode()
        ctk.set_appearance_mode(mode)
        super().__init__()
        self.appearance_mode = mode
        self.appearance_var = tk.BooleanVar(value=mode == "dark")
        self.appearance_switch: ctk.CTkSwitch | None = None
        self.appearance_sun: ctk.CTkLabel | None = None
        self.appearance_moon: ctk.CTkLabel | None = None
        self.data_dir = Path(data_dir)
        self.library = Library(self.data_dir / "books.txt", self.data_dir / "users.txt")
        self.page = 0
        self.user_page = 0
        self.current_view = "dashboard"
        self.sidebar_expanded = False
        self.sidebar: ctk.CTkFrame | None = None
        self.sidebar_toggle_item: SidebarItem | None = None
        self.nav_items: dict[str, SidebarItem] = {}
        self.sidebar_actions: list[SidebarItem] = []
        self.palette_labels: list[tuple[theme.Color, ctk.CTkLabel]] = []
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)

        self.title("Bibliothèque personnelle")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(fg_color=theme.BACKGROUND)

        self._build_shell()
        self._load_data()
        self.show_view("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_shell(self) -> None:
        topbar = ctk.CTkFrame(self, fg_color=theme.PRIMARY, corner_radius=0, height=82)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar,
            text="Bibliothèque personnelle",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT_ON_PRIMARY,
        ).pack(side="left", padx=(28, 12))
        ctk.CTkLabel(
            topbar,
            text="Gestion des livres, usagers et emprunts",
            font=theme.FONT_SMALL,
            text_color=theme.ACCENT,
        ).pack(side="left")

        topbar_actions = ctk.CTkFrame(topbar, fg_color="transparent")
        topbar_actions.pack(side="right", padx=26)
        appearance = ctk.CTkFrame(topbar_actions, fg_color="transparent")
        appearance.pack(side="left", padx=(0, 16))
        self.appearance_sun = ctk.CTkLabel(
            appearance,
            text="☀",
            font=(theme.FONT_FAMILY, 22),
            text_color=theme.ACCENT,
            cursor="hand2",
        )
        self.appearance_sun.pack(side="left")
        self.appearance_sun.bind(
            "<Button-1>", lambda _event: self._set_appearance_mode("light")
        )
        self.appearance_switch = ctk.CTkSwitch(
            appearance,
            text="",
            variable=self.appearance_var,
            onvalue=True,
            offvalue=False,
            command=self._on_appearance_switch,
            width=56,
            height=34,
            switch_width=48,
            switch_height=26,
            corner_radius=13,
            border_width=1,
            border_color=theme.ACCENT,
            fg_color=theme.BORDER,
            progress_color=theme.SECONDARY,
            button_color=theme.SURFACE,
            button_hover_color=theme.ACCENT,
        )
        self.appearance_switch.pack(side="left", padx=8)
        self.appearance_moon = ctk.CTkLabel(
            appearance,
            text="☾",
            font=(theme.FONT_FAMILY, 22),
            text_color=theme.ACCENT,
            cursor="hand2",
        )
        self.appearance_moon.pack(side="left")
        self.appearance_moon.bind(
            "<Button-1>", lambda _event: self._set_appearance_mode("dark")
        )

        self.palette_frame = ctk.CTkFrame(topbar_actions, fg_color="transparent")
        self.palette_frame.pack(side="left")
        for color in (theme.SURFACE, theme.BACKGROUND, theme.ACCENT, theme.SECONDARY, theme.PRIMARY):
            label = ctk.CTkLabel(
                self.palette_frame,
                text="●",
                font=(theme.FONT_FAMILY, 22),
                text_color=color,
            )
            self.palette_labels.append((color, label))

        body = ctk.CTkFrame(self, fg_color=theme.BACKGROUND, corner_radius=0)
        body.pack(fill="both", expand=True)
        body.pack_propagate(False)

        sidebar_width = 200 if self.sidebar_expanded else 72
        self.sidebar = ctk.CTkFrame(
            body, fg_color=theme.BACKGROUND, corner_radius=0, width=sidebar_width
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.sidebar.bind("<Button-1>", lambda _event: self._toggle_sidebar())

        self.sidebar_toggle_item = SidebarItem(
            self.sidebar,
            self,
            "toggle",
            "Replier",
            "toggle_expand",
            self._toggle_sidebar,
        )
        self.sidebar_toggle_item.pack(padx=8, pady=(8, 0))

        nav = [
            ("dashboard", "dashboard", "Accueil"),
            ("books", "books", "Livres"),
            ("users", "users", "Usagers"),
            ("stats", "stats", "Stats"),
        ]
        for key, icon, label in nav:
            item = SidebarItem(
                self.sidebar,
                self,
                key,
                label,
                icon,
                lambda name=key: self.show_view(name),
            )
            item.pack(padx=8, pady=(8, 0))
            self.nav_items[key] = item

        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_footer.pack(side="bottom", fill="x", pady=(0, 12))
        actions = [
            ("save", "Sauver", "save", "save", self.save_manually),
            ("backup", "Backup", "backup", "backup", self.backup),
            ("quit", "Quitter", "quit", "quit", self._on_close),
        ]
        for key, label, icon, role, command in actions:
            item = SidebarItem(
                sidebar_footer,
                self,
                key,
                label,
                icon,
                command,
                role=role,
            )
            item.pack(padx=8, pady=4)
            self.sidebar_actions.append(item)

        main = ctk.CTkFrame(body, fg_color=theme.BACKGROUND, corner_radius=0)
        main.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=(0, 14))
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(main, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(16, 12))
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_group = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.search_group.grid(row=0, column=0, sticky="ew")
        self.search_group.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(
            self.search_group,
            textvariable=self.search_var,
            placeholder_text="Rechercher un titre, un auteur ou un ISBN…",
            height=48,
            corner_radius=16,
            font=theme.FONT_BODY,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<Return>", lambda _event: self.show_view("books"))
        self.search_button = ctk.CTkButton(
            self.search_group,
            text="Rechercher",
            width=124,
            height=48,
            corner_radius=16,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.PRIMARY,
            hover_color=theme.SECONDARY,
            command=lambda: self.show_view("books"),
        )
        self.search_button.grid(row=0, column=1, padx=(12, 0))
        self.add_book_button = ctk.CTkButton(
            toolbar,
            text="+  Livre",
            width=122,
            height=48,
            corner_radius=16,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SECONDARY,
            hover_color=theme.PRIMARY,
            command=self.open_add_book,
        )
        self.add_book_button.grid(row=0, column=1, padx=(12, 0))
        self.add_user_button = ctk.CTkButton(
            toolbar,
            text="+  Usager",
            width=122,
            height=48,
            corner_radius=16,
            font=theme.FONT_BODY_BOLD,
            fg_color=theme.SECONDARY,
            hover_color=theme.PRIMARY,
            command=self.open_add_user,
        )
        self.add_user_button.grid(row=0, column=2, padx=(12, 0))

        self.view_frame = ctk.CTkFrame(main, fg_color="transparent", corner_radius=0)
        self.view_frame.grid(row=1, column=0, sticky="nsew")

        self._refresh_appearance_controls()
        self._render_palette()

    def _set_appearance_mode(self, mode: str) -> None:
        if mode not in {"light", "dark"}:
            return
        self.appearance_mode = mode
        self.appearance_var.set(mode == "dark")
        ctk.set_appearance_mode(mode)
        save_appearance_mode(mode)
        self._refresh_appearance_controls()
        self._render_palette()
        self._refresh_sidebar_theme()

    def _refresh_appearance_controls(self) -> None:
        if self.appearance_sun is not None:
            self.appearance_sun.configure(
                text_color=theme.TEXT_ON_PRIMARY
                if self.appearance_mode == "light"
                else theme.ACCENT
            )
        if self.appearance_moon is not None:
            self.appearance_moon.configure(
                text_color=theme.TEXT_ON_PRIMARY
                if self.appearance_mode == "dark"
                else theme.ACCENT
            )

    def _render_palette(self) -> None:
        for _color, label in self.palette_labels:
            label.pack_forget()
        ordered = sorted(
            self.palette_labels,
            key=lambda item: color_luminance(
                resolve_color(item[0], self.appearance_mode)
            ),
            reverse=self.appearance_mode == "light",
        )
        for _color, label in ordered:
            label.pack(side="left", padx=3)

    def _sidebar_items(self) -> list[SidebarItem]:
        items = list(self.nav_items.values()) + self.sidebar_actions
        if self.sidebar_toggle_item is not None:
            items.append(self.sidebar_toggle_item)
        return items

    def _refresh_sidebar_theme(self) -> None:
        for item in self._sidebar_items():
            item.refresh_theme()

    def _on_appearance_switch(self) -> None:
        self._set_appearance_mode(
            "dark" if self.appearance_var.get() else "light"
        )

    def _toggle_sidebar(self) -> None:
        self.sidebar_expanded = not self.sidebar_expanded
        if self.sidebar is not None:
            self.sidebar.configure(width=200 if self.sidebar_expanded else 72)
        for item in self._sidebar_items():
            item.set_expanded(self.sidebar_expanded)
        if self.sidebar_toggle_item is not None:
            self.sidebar_toggle_item.set_icon(
                "toggle_collapse" if self.sidebar_expanded else "toggle_expand"
            )
            self.sidebar_toggle_item.set_label("Replier")

    def _load_data(self) -> None:
        try:
            self.library.load()
        except (LibraryError, OSError) as exc:
            self.after(
                80,
                lambda: messagebox.showerror(
                    "Chargement impossible",
                    f"Les données n'ont pas pu être chargées :\n{exc}",
                    parent=self,
                ),
            )

    def filtered_books(self) -> list[Book]:
        return self.library.search_books(self.search_var.get())

    def show_view(self, name: str) -> None:
        self.current_view = name
        if name == "books":
            self.search_group.grid()
        else:
            self.search_group.grid_remove()
        for key, item in self.nav_items.items():
            item.set_active(key == name)
        for child in self.view_frame.winfo_children():
            child.destroy()
        views = {
            "dashboard": DashboardView,
            "books": BooksView,
            "users": UsersView,
            "stats": StatsView,
        }
        view = views[name](self.view_frame, self)
        view.pack(fill="both", expand=True)

    def refresh(self, navigate: str | None = None) -> None:
        self.show_view(navigate or self.current_view)

    def change_page(self, delta: int) -> None:
        self.page += delta
        self.refresh(navigate="books")

    def change_user_page(self, delta: int) -> None:
        self.user_page += delta
        self.refresh(navigate="users")

    def _on_search_changed(self, *_args) -> None:
        if self.current_view == "books":
            self.page = 0
            self.refresh()

    def persist(self) -> bool:
        try:
            self.library.save()
        except OSError as exc:
            messagebox.showerror(
                "Sauvegarde impossible",
                f"Les données n'ont pas pu être enregistrées :\n{exc}",
                parent=self,
            )
            return False
        return True

    def save_manually(self) -> None:
        self.persist()

    def backup(self) -> None:
        if not self.persist():
            return
        try:
            backups = self.library.create_backup()
        except OSError as exc:
            messagebox.showerror(
                "Sauvegarde impossible",
                f"Les fichiers de sauvegarde n'ont pas pu être créés :\n{exc}",
                parent=self,
            )
            return
        if backups:
            details = "\n".join(str(path) for path in backups)
            messagebox.showinfo(
                "Sauvegarde créée",
                f"Fichiers de sauvegarde créés :\n{details}",
                parent=self,
            )
        else:
            messagebox.showinfo(
                "Aucune donnée",
                "Aucun fichier de données à sauvegarder.",
                parent=self,
            )

    def open_add_book(self) -> None:
        AddBookDialog(self)

    def open_add_user(self) -> None:
        AddUserDialog(self)

    def borrow_book(self, book: Book) -> None:
        if not self.library.users:
            messagebox.showinfo(
                "Aucun usager",
                "Ajoutez d'abord un utilisateur avant de créer un emprunt.",
                parent=self,
            )
            return
        BorrowDialog(self, book)

    def return_book(self, book: Book) -> None:
        if not messagebox.askyesno(
            "Retourner un livre",
            f"Confirmer le retour de « {book.title} » ?",
            parent=self,
        ):
            return
        try:
            self.library.return_book(book.isbn)
        except LibraryError as exc:
            messagebox.showerror("Retour impossible", str(exc), parent=self)
            return
        if not self.persist():
            return
        self.refresh()

    def delete_book(self, book: Book) -> None:
        warning = ""
        if not book.available:
            warning = f"\n\nCe livre est emprunté par {book.borrower_id}."
        if not messagebox.askyesno(
            "Supprimer un livre",
            f"Supprimer définitivement « {book.title} » ?{warning}",
            parent=self,
        ):
            return
        try:
            self.library.remove_book(book.isbn)
        except LibraryError as exc:
            messagebox.showerror("Suppression impossible", str(exc), parent=self)
            return
        if not self.persist():
            return
        self.refresh()

    def _on_close(self) -> None:
        try:
            self.library.save()
        except OSError as exc:
            messagebox.showerror(
                "Sauvegarde impossible",
                f"Les données n'ont pas pu être enregistrées :\n{exc}",
                parent=self,
            )
            if not messagebox.askyesno(
                "Quitter sans sauvegarder",
                "Quitter malgré l'échec de la sauvegarde ?",
                parent=self,
            ):
                return
        self.destroy()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bibliothèque personnelle en CustomTkinter.")
    parser.add_argument(
        "-d",
        "--data-dir",
        type=Path,
        default=default_data_dir(),
        help="répertoire contenant books.txt et users.txt",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    if not data_dir.is_dir():
        print(f"Erreur : le répertoire {data_dir} n'existe pas.", file=sys.stderr)
        return 1

    app = LibraryApp(data_dir)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
