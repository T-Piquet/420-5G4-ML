"""Liste des emprunts en cours et actions d'emprunt / retour."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from gui.components.dialogs import CheckoutDialog, show_error
from gui.components.table import ScrollableTable, TableColumn
from gui.service import LibraryError, LibraryService


class LoansView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        service: LibraryService,
        on_mutation: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.service = service
        self.on_mutation = on_mutation
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        toolbar.grid_columnconfigure(0, weight=1)

        self.count_label = ctk.CTkLabel(
            toolbar,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        )
        self.count_label.grid(row=0, column=0, sticky="w")

        self.checkout_button = ctk.CTkButton(
            toolbar,
            text="Nouvel emprunt",
            width=150,
            height=36,
            command=self._open_checkout_dialog,
        )
        self.checkout_button.grid(row=0, column=1, padx=(10, 10))

        self.return_button = ctk.CTkButton(
            toolbar,
            text="Retourner le livre sélectionné",
            width=240,
            height=36,
            fg_color="#b45309",
            hover_color="#92400e",
            state="disabled",
            command=self._return_selected,
        )
        self.return_button.grid(row=0, column=2, padx=(0, 10))

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Rafraîchir",
            width=110,
            height=36,
            command=self.refresh,
        )
        self.refresh_button.grid(row=0, column=3)

        ctk.CTkLabel(
            self,
            text="Cliquez sur une ligne pour sélectionner un emprunt à retourner.",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray60"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

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
            on_select=self._on_selection,
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

    def _on_selection(self, row: dict[str, object] | None) -> None:
        self.return_button.configure(
            state="normal" if row is not None else "disabled"
        )

    def _open_checkout_dialog(self) -> None:
        books = self.service.get_available_books()
        users = self.service.get_users()

        if not books:
            show_error(
                self,
                "Aucun livre disponible pour un emprunt. "
                "Ajoutez un livre ou attendez un retour.",
                title="Aucun livre disponible",
            )
            return
        if not users:
            show_error(
                self,
                "Aucun adhérent enregistré. Ajoutez d'abord un adhérent.",
                title="Aucun adhérent",
            )
            return

        CheckoutDialog(self, books, users, on_submit=self._checkout)

    def _checkout(self, isbn: str, user_id: str) -> None:
        self.service.checkout_book(isbn, user_id)
        self.on_mutation("Emprunt enregistré avec succès.")

    def _return_selected(self) -> None:
        row = self.table.get_selected()
        if row is None:
            show_error(
                self,
                "Veuillez d'abord sélectionner un emprunt dans la liste.",
                title="Aucune sélection",
            )
            return

        isbn = str(row.get("isbn", ""))
        title = str(row.get("book_title", ""))
        try:
            self.service.return_book(isbn)
        except LibraryError as exc:
            show_error(self, str(exc), title="Retour impossible")
            return

        self.on_mutation(f"Livre « {title} » retourné.")
