"""Books catalog page connected to BibliothequeAPI."""

import customtkinter as ctk

from theme import COLORS, FONTS, RADIUS
from ui.icons import ICON_ADD, ICON_SEARCH
from ui.pages.base import BasePage
from ui.table import ScrollableList
from ui.widgets import ItemRowCard


class AddBookDialog(ctk.CTkToplevel):
    """Modal dialog to add a new book."""

    def __init__(self, master, on_submit) -> None:
        super().__init__(master)
        self.title("Ajouter un livre")
        self.geometry("360x260")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_submit = on_submit

        self.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Titre")
        self.title_entry.grid(row=0, column=0, padx=20, pady=(20, 8), sticky="ew")

        self.author_entry = ctk.CTkEntry(self, placeholder_text="Auteur")
        self.author_entry.grid(row=1, column=0, padx=20, pady=8, sticky="ew")

        self.isbn_entry = ctk.CTkEntry(self, placeholder_text="ISBN")
        self.isbn_entry.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.error_label = ctk.CTkLabel(self, text="", text_color=COLORS["danger"], font=FONTS["small"])
        self.error_label.grid(row=3, column=0, padx=20, pady=4, sticky="w")

        ctk.CTkButton(self, text="Ajouter", command=self._submit).grid(
            row=4, column=0, padx=20, pady=(8, 16), sticky="e"
        )

    def _submit(self) -> None:
        ok, msg = self._on_submit(
            self.title_entry.get(),
            self.author_entry.get(),
            self.isbn_entry.get(),
        )
        if ok:
            self.destroy()
        else:
            self.error_label.configure(text=msg)


class BooksPage(BasePage):
    """Displays the book catalog with search (ISBN/Titre/Auteur), availability filter, and actions."""

    def __init__(self, master, api) -> None:
        super().__init__(master, api)
        self.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")

        self.search_mode_var = ctk.StringVar(value="Tout")
        self.search_mode = ctk.CTkOptionMenu(
            toolbar,
            values=["Tout", "ISBN", "Titre", "Auteur"],
            variable=self.search_mode_var,
            width=95,
            height=34,
            corner_radius=RADIUS["button"],
            fg_color=COLORS["bg_button"],
            button_color=COLORS["bg_button_hover"],
            text_color=COLORS["text_primary"],
            command=lambda _: self.refresh(),
        )
        self.search_mode.grid(row=0, column=0, padx=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text=ICON_SEARCH,
            width=190,
            height=34,
            corner_radius=RADIUS["input"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_width=0,
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 14))
        self.search_var.trace_add("write", lambda *_: self.refresh())

        self.add_btn = ctk.CTkButton(
            toolbar,
            text=ICON_ADD,
            width=100,
            height=34,
            corner_radius=RADIUS["button"],
            fg_color=COLORS["bg_button"],
            hover_color=COLORS["bg_button_hover"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
            command=self._on_add_clicked,
        )
        self.add_btn.grid(row=0, column=2, padx=(0, 14))

        self.available_only_var = ctk.BooleanVar(value=False)
        self.available_check = ctk.CTkCheckBox(
            toolbar,
            text="Livre disponible",
            variable=self.available_only_var,
            text_color=COLORS["text_light"],
            font=FONTS["body"],
            fg_color=COLORS["bg_button"],
            checkmark_color=COLORS["text_primary"],
            command=self.refresh,
        )
        self.available_check.grid(row=0, column=3, padx=(0, 8))

        self.list_frame = ScrollableList(self)
        self.list_frame.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="nsew")

        self.feedback_label = ctk.CTkLabel(
            self, text="", font=FONTS["small"], text_color=COLORS["text_light"], anchor="w"
        )
        self.feedback_label.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")

    def refresh(self) -> None:
        self.list_frame.clear()
        query = self.search_var.get().strip()
        mode = self.search_mode_var.get()
        only_avail = self.available_only_var.get()

        if not query:
            books = self.api.get_available_books() if only_avail else self.api.get_all_books()
        elif mode == "ISBN":
            found = self.api.find_book_by_isbn(query)
            books = [found] if found is not None else []
        elif mode == "Titre":
            books = self.api.search_books_by_title(query)
        elif mode == "Auteur":
            books = self.api.search_books_by_author(query)
        else:
            q_lower = query.lower()
            base = self.api.get_available_books() if only_avail else self.api.get_all_books()
            books = [
                b for b in base
                if q_lower in b.isbn.lower()
                or q_lower in b.title.lower()
                or q_lower in b.author.lower()
            ]

        for book in books:
            if only_avail and not book.is_available:
                continue
            status = "Disponible" if book.is_available else f"Emprunté ({book.borrower_id})"
            text = f"{book.title} — {book.author} | ISBN: {book.isbn} | {status}"
            row = ItemRowCard(
                self.list_frame,
                text=text,
                on_delete=lambda isbn=book.isbn: self._on_delete_clicked(isbn),
            )
            self.list_frame.add_row(row)

    def _on_add_clicked(self) -> None:
        def submit(title: str, author: str, isbn: str):
            ok, msg = self.api.add_book(title, author, isbn)
            if ok:
                self.feedback_label.configure(text=msg)
                self.refresh()
            return ok, msg

        AddBookDialog(self, submit)

    def _on_delete_clicked(self, isbn: str) -> None:
        ok, msg = self.api.remove_book(isbn)
        self.feedback_label.configure(text=msg)
        if ok:
            self.refresh()
