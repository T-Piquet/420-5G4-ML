"""Onglet Emprunts : emprunt et retour de livres."""

from __future__ import annotations

import customtkinter as ctk

NO_BOOK = "Aucun livre disponible"
NO_LOAN = "Aucun livre emprunté"
NO_USER = "Aucun utilisateur"


class LoansView(ctk.CTkFrame):
    def __init__(self, master, service, on_status, on_data_changed) -> None:
        super().__init__(master, fg_color="transparent")

        self.service = service
        self.on_status = on_status
        self.on_data_changed = on_data_changed

        self._available_options: dict[str, str] = {}
        self._borrowed_options: dict[str, str] = {}
        self._user_options: dict[str, str] = {}

        self.grid_columnconfigure(0, weight=1)

        self._build_checkout_section()
        self._build_return_section()

        self.refresh()

    # Construction de l'interface

    def _build_checkout_section(self) -> None:
        section = ctk.CTkFrame(self)
        section.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        section.grid_columnconfigure(1, weight=1)
        section.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            section,
            text="Emprunter un livre",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(section, text="Livre").grid(
            row=1, column=0, padx=(8, 6), pady=4, sticky="w"
        )
        self.book_menu = ctk.CTkOptionMenu(section, values=[NO_BOOK])
        self.book_menu.grid(row=1, column=1, padx=(0, 12), pady=4, sticky="ew")

        ctk.CTkLabel(section, text="Utilisateur").grid(
            row=1, column=2, padx=(0, 6), pady=4, sticky="w"
        )
        self.user_menu = ctk.CTkOptionMenu(section, values=[NO_USER])
        self.user_menu.grid(row=1, column=3, padx=(0, 8), pady=4, sticky="ew")

        buttons = ctk.CTkFrame(section, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=4, sticky="e", padx=8, pady=(4, 8))

        ctk.CTkButton(
            buttons, text="Emprunter", width=120, command=self._on_check_out
        ).grid(row=0, column=0)

    def _build_return_section(self) -> None:
        section = ctk.CTkFrame(self)
        section.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))
        section.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            section,
            text="Retourner un livre",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(section, text="Livre").grid(
            row=1, column=0, padx=(8, 6), pady=4, sticky="w"
        )
        self.return_menu = ctk.CTkOptionMenu(section, values=[NO_LOAN])
        self.return_menu.grid(row=1, column=1, padx=(0, 8), pady=4, sticky="ew")

        buttons = ctk.CTkFrame(section, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=2, sticky="e", padx=8, pady=(4, 8))

        ctk.CTkButton(
            buttons, text="Retourner", width=120, command=self._on_return
        ).grid(row=0, column=0)

    # Donnees

    @staticmethod
    def _book_label(book: dict) -> str:
        return f"{book['title']} — {book['author']} ({book['isbn']})"

    @staticmethod
    def _user_label(user: dict) -> str:
        return f"{user['name']} ({user['user_id']})"

    def refresh(self) -> None:
        available_books = self.service.get_available_books()
        borrowed_books = [
            book for book in self.service.get_books() if not book["available"]
        ]
        users = self.service.get_users()

        self._available_options = {
            self._book_label(book): book["isbn"] for book in available_books
        }
        self._borrowed_options = {
            self._book_label(book): book["isbn"] for book in borrowed_books
        }
        self._user_options = {
            self._user_label(user): user["user_id"] for user in users
        }

        self._update_menu(self.book_menu, list(self._available_options), NO_BOOK)
        self._update_menu(
            self.return_menu, list(self._borrowed_options), NO_LOAN
        )
        self._update_menu(self.user_menu, list(self._user_options), NO_USER)

    @staticmethod
    def _update_menu(menu: ctk.CTkOptionMenu, values: list[str], empty: str) -> None:
        menu.configure(values=values or [empty])
        menu.set(values[0] if values else empty)

    # Actions

    def _on_check_out(self) -> None:
        if not self._available_options:
            self.on_status("Aucun livre disponible pour l'emprunt.")
            return
        if not self._user_options:
            self.on_status("Aucun utilisateur enregistré.")
            return

        isbn = self._available_options.get(self.book_menu.get())
        user_id = self._user_options.get(self.user_menu.get())
        if isbn is None:
            self.on_status("Veuillez sélectionner un livre à emprunter.")
            return
        if user_id is None:
            self.on_status("Veuillez sélectionner un utilisateur.")
            return

        book = self.service.find_book(isbn)
        user = self.service.find_user(user_id)

        if self.service.check_out(isbn, user_id):
            self.refresh()
            self.on_data_changed()
            self.on_status(
                f"Livre emprunté : {book['title']} ({isbn}) par "
                f"{user['name']} ({user_id})."
            )
        else:
            self.on_status(f"Impossible d'emprunter le livre {isbn}.")

    def _on_return(self) -> None:
        if not self._borrowed_options:
            self.on_status("Aucun livre emprunté à retourner.")
            return

        isbn = self._borrowed_options.get(self.return_menu.get())
        if isbn is None:
            self.on_status("Veuillez sélectionner un livre à retourner.")
            return

        book = self.service.find_book(isbn)

        if self.service.return_book(isbn):
            self.refresh()
            self.on_data_changed()
            self.on_status(f"Livre retourné : {book['title']} ({isbn}).")
        else:
            self.on_status(f"Impossible de retourner le livre {isbn}.")
