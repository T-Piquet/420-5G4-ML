import customtkinter as ctk

from gui.service import ServiceError

PLACEHOLDER_BOOK = "Sélectionner un livre"
PLACEHOLDER_USER = "Sélectionner un utilisateur"
PLACEHOLDER_RETURN = "Sélectionner un livre emprunté"


class BorrowsView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._book_values = {}
        self._user_values = {}
        self._return_values = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="borrows")

        borrow_frame = ctk.CTkFrame(self)
        borrow_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        borrow_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            borrow_frame,
            text="Emprunter un livre",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        self.borrow_book_menu = ctk.CTkOptionMenu(
            borrow_frame,
            values=[PLACEHOLDER_BOOK],
            command=lambda _: self._update_buttons(),
        )
        self.borrow_book_menu.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        self.borrow_user_menu = ctk.CTkOptionMenu(
            borrow_frame,
            values=[PLACEHOLDER_USER],
            command=lambda _: self._update_buttons(),
        )
        self.borrow_user_menu.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        self.borrow_button = ctk.CTkButton(
            borrow_frame,
            text="Emprunter",
            state="disabled",
            command=self.borrow_book,
        )
        self.borrow_button.grid(row=3, column=0, sticky="ew", padx=15, pady=(10, 15))

        return_frame = ctk.CTkFrame(self)
        return_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        return_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            return_frame,
            text="Retourner un livre",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        self.return_menu = ctk.CTkOptionMenu(
            return_frame,
            values=[PLACEHOLDER_RETURN],
            command=lambda _: self._update_buttons(),
        )
        self.return_menu.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        self.return_button = ctk.CTkButton(
            return_frame,
            text="Retourner",
            state="disabled",
            command=self.return_book,
        )
        self.return_button.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 15))

        self.refresh()

    def refresh(self):
        """Recharge les listes de livres et d'utilisateurs."""
        self._book_values = {
            f"{book.title} — {book.isbn}": book.isbn
            for book in self.app.service.available_books
        }
        self._user_values = {
            f"{user.name} ({user.user_id})": user.user_id
            for user in self.app.service.users
        }
        self._return_values = {
            f"{book.title} — {book.isbn} ({book.borrower_id})": book.isbn
            for book in self.app.service.checked_out_books
        }

        self.borrow_book_menu.configure(
            values=list(self._book_values) or [PLACEHOLDER_BOOK]
        )
        self.borrow_book_menu.set(PLACEHOLDER_BOOK)
        self.borrow_user_menu.configure(
            values=list(self._user_values) or [PLACEHOLDER_USER]
        )
        self.borrow_user_menu.set(PLACEHOLDER_USER)
        self.return_menu.configure(
            values=list(self._return_values) or [PLACEHOLDER_RETURN]
        )
        self.return_menu.set(PLACEHOLDER_RETURN)

        self._update_buttons()

    def _update_buttons(self):
        borrow_ready = (
            self.borrow_book_menu.get() in self._book_values
            and self.borrow_user_menu.get() in self._user_values
        )
        self.borrow_button.configure(state="normal" if borrow_ready else "disabled")

        return_ready = self.return_menu.get() in self._return_values
        self.return_button.configure(state="normal" if return_ready else "disabled")

    def borrow_book(self):
        """Emprunte le livre et l'utilisateur sélectionnés."""
        isbn = self._book_values.get(self.borrow_book_menu.get())
        user_id = self._user_values.get(self.borrow_user_menu.get())
        if not isbn or not user_id:
            return

        try:
            self.app.service.check_out_book(isbn, user_id)
        except ServiceError as error:
            self.app.show_error(str(error))
            self.refresh()
            return

        self.app.mark_unsaved()
        self.app.show_success(f"Livre {isbn} emprunté par {user_id}.")
        self.refresh()

    def return_book(self):
        """Retourne le livre sélectionné."""
        isbn = self._return_values.get(self.return_menu.get())
        if not isbn:
            return

        try:
            self.app.service.return_book(isbn)
        except ServiceError as error:
            self.app.show_error(str(error))
            self.refresh()
            return

        self.app.mark_unsaved()
        self.app.show_success(f"Livre {isbn} retourné.")
        self.refresh()
