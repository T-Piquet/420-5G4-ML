"""Catalogue des livres avec recherche et filtre de disponibilité."""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from gui.components.table import ScrollableTable, TableColumn
from gui.service import LibraryService


class CatalogueView(ctk.CTkFrame):
    def __init__(self, master, service: LibraryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.service = service
        self._books = []
        self._borrower_names: dict[str, str] = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Rechercher par titre ou auteur…",
            textvariable=self.search_var,
            height=36,
        )
        self.search_entry.grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )

        self.filter_var = tk.StringVar(value="Tous")
        self.filter_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["Tous", "Disponibles", "Empruntés"],
            variable=self.filter_var,
            command=lambda _value: self._apply_filter(),
            width=140,
            height=36,
        )
        self.filter_menu.grid(row=0, column=1, padx=(0, 10))

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Rafraîchir",
            width=110,
            height=36,
            command=self.refresh,
        )
        self.refresh_button.grid(row=0, column=2)

        self.count_label = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        )
        self.count_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        self.table = ScrollableTable(
            self,
            columns=[
                TableColumn("title", "Titre", weight=3, wrap=260),
                TableColumn("author", "Auteur", weight=2, wrap=170),
                TableColumn("isbn", "ISBN", weight=2, wrap=150),
                TableColumn("availability", "Disponibilité", weight=1, wrap=110),
                TableColumn("borrower", "Emprunteur", weight=2, wrap=130),
            ],
            status_key="availability",
            status_colors={
                "Disponible": ("#15803d", "#4ade80"),
                "Emprunté": ("#b45309", "#fbbf24"),
            },
            empty_text="Aucun livre ne correspond à cette recherche.",
        )
        self.table.grid(row=2, column=0, sticky="nsew")

        self.search_var.trace_add("write", lambda *_args: self._apply_filter())

    def refresh(self) -> None:
        self._books = self.service.get_books()
        self._borrower_names = {
            user.user_id: user.name for user in self.service.get_users()
        }
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self.search_var.get().strip()
        books = (
            self.service.search_books(query) if query else self._books
        )

        selected_filter = self.filter_var.get()
        if selected_filter == "Disponibles":
            books = [book for book in books if book.available]
        elif selected_filter == "Empruntés":
            books = [book for book in books if not book.available]

        rows = [
            {
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "availability": (
                    "Disponible" if book.available else "Emprunté"
                ),
                "borrower": (
                    self._borrower_names.get(
                        book.borrower_id, book.borrower_id
                    )
                    if not book.available
                    else "—"
                ),
            }
            for book in books
        ]
        self.table.set_rows(rows)
        self.count_label.configure(
            text=f"{len(rows)} livre(s) affiché(s)"
        )
