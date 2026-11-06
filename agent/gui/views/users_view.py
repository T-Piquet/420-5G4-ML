"""Liste des adhérents et de leurs emprunts."""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from gui.components.table import ScrollableTable, TableColumn
from gui.service import LibraryService


class UsersView(ctk.CTkFrame):
    def __init__(self, master, service: LibraryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.service = service
        self._users = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Rechercher par nom ou identifiant…",
            textvariable=self.search_var,
            height=36,
        )
        self.search_entry.grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Rafraîchir",
            width=110,
            height=36,
            command=self.refresh,
        )
        self.refresh_button.grid(row=0, column=1)

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
                TableColumn("name", "Nom", weight=2, wrap=160),
                TableColumn("user_id", "Identifiant", weight=1, wrap=110),
                TableColumn("borrowed_count", "Emprunts", weight=1, wrap=90),
                TableColumn("borrowed_titles", "Livres empruntés", weight=4, wrap=380),
            ],
            empty_text="Aucun adhérent enregistré.",
        )
        self.table.grid(row=2, column=0, sticky="nsew")

        self.search_var.trace_add("write", lambda *_args: self._apply_filter())

    def refresh(self) -> None:
        self._users = self.service.get_users()
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self.search_var.get().strip().casefold()
        users = self._users
        if query:
            users = [
                user
                for user in users
                if query in user.name.casefold()
                or query in user.user_id.casefold()
            ]

        rows = [
            {
                "name": user.name,
                "user_id": user.user_id,
                "borrowed_count": len(user.borrowed_books),
                "borrowed_titles": (
                    " • ".join(user.borrowed_titles)
                    if user.borrowed_titles
                    else "Aucun"
                ),
            }
            for user in users
        ]
        self.table.set_rows(rows)
        self.count_label.configure(
            text=f"{len(rows)} adhérent(s) affiché(s)"
        )
