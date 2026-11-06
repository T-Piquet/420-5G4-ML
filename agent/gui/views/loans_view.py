"""Liste des emprunts en cours avec l'identité de l'emprunteur."""

from __future__ import annotations

import customtkinter as ctk

from gui.components.table import ScrollableTable, TableColumn
from gui.service import LibraryService


class LoansView(ctk.CTkFrame):
    def __init__(self, master, service: LibraryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.service = service
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        self.count_label = ctk.CTkLabel(
            toolbar,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        )
        self.count_label.grid(row=0, column=0, sticky="w")

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Rafraîchir",
            width=110,
            height=36,
            command=self.refresh,
        )
        self.refresh_button.grid(row=0, column=1)

        self.table = ScrollableTable(
            self,
            columns=[
                TableColumn("book_title", "Livre", weight=3, wrap=240),
                TableColumn("author", "Auteur", weight=2, wrap=160),
                TableColumn("isbn", "ISBN", weight=2, wrap=140),
                TableColumn("borrower_name", "Emprunteur", weight=2, wrap=150),
                TableColumn("borrower_id", "Identifiant", weight=1, wrap=110),
            ],
            empty_text="Aucun emprunt en cours.",
        )
        self.table.grid(row=2, column=0, sticky="nsew")

    def refresh(self) -> None:
        loans = self.service.get_loans()
        rows = [
            {
                "book_title": loan.book_title,
                "author": loan.author,
                "isbn": loan.isbn,
                "borrower_name": loan.borrower_name,
                "borrower_id": loan.borrower_id,
            }
            for loan in loans
        ]
        self.table.set_rows(rows)
        self.count_label.configure(
            text=f"{len(rows)} emprunt(s) en cours"
        )
