import tkinter as tk
import warnings
import customtkinter as ctk
from tkinter import messagebox

from gui.service import ServiceError


def make_trash_icon(size=20, color="#ffffff"):
    icon = tk.PhotoImage(width=size, height=size)
    icon.put(color, to=(8, 1, 12, 3))
    icon.put(color, to=(4, 3, 16, 5))
    icon.put(color, to=(5, 6, 15, 8))
    icon.put(color, to=(5, 6, 7, 18))
    icon.put(color, to=(13, 6, 15, 18))
    icon.put(color, to=(5, 16, 15, 18))
    icon.put(color, to=(8, 9, 9, 15))
    icon.put(color, to=(11, 9, 12, 15))
    return icon


class BooksView(ctk.CTkFrame):
    COLUMNS = ["Titre", "Auteur", "ISBN", "Disponibilité", "Emprunteur"]
    WEIGHTS = [3, 2, 2, 1, 1]

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._trash_icon = make_trash_icon()
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ctk.CTkEntry(
            top, textvariable=self.search_var, placeholder_text="Rechercher..."
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.filter_var = tk.StringVar(value="Tous")
        ctk.CTkOptionMenu(
            top,
            variable=self.filter_var,
            values=["Tous", "Disponible", "Emprunté"],
            command=lambda _: self.refresh(),
        ).grid(row=0, column=1)

        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(container, fg_color=("gray85", "gray25"))
        header.grid(row=0, column=0, sticky="ew")
        for index, (column, weight) in enumerate(zip(self.COLUMNS, self.WEIGHTS)):
            header.grid_columnconfigure(index, weight=weight, uniform="books")
            ctk.CTkLabel(header, text=column, anchor="w").grid(
                row=0, column=index, sticky="ew", padx=8, pady=6
            )
        header.grid_columnconfigure(len(self.COLUMNS), minsize=70)

        self.rows = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.rows.grid(row=1, column=0, sticky="nsew")
        self.rows.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            container,
            text="Aucun livre trouvé",
            font=ctk.CTkFont(size=16, weight="bold"),
        )

        self.refresh()

        self.add_button = ctk.CTkButton(
            self, text="Ajouter un livre", command=self.open_add_dialog
        )
        self.add_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

    def refresh(self):
        """Recharge la liste avec les livres filtrés et triés."""
        query = self.search_var.get().strip().casefold()
        filter_status = self.filter_var.get()

        books = self.app.service.books
        if filter_status == "Disponible":
            books = [book for book in books if book.is_available]
        elif filter_status == "Emprunté":
            books = [book for book in books if not book.is_available]

        if query:
            books = [
                book
                for book in books
                if query in book.title.casefold() or query in book.author.casefold()
            ]

        for child in self.rows.winfo_children():
            child.destroy()

        for index, book in enumerate(books):
            row = ctk.CTkFrame(self.rows)
            row.grid(row=index, column=0, sticky="ew", pady=2)
            for column, weight in enumerate(self.WEIGHTS):
                row.grid_columnconfigure(column, weight=weight, uniform="books")
            row.grid_columnconfigure(len(self.WEIGHTS), minsize=70)

            values = [
                book.title,
                book.author,
                book.isbn,
                "Oui" if book.is_available else "Non",
                book.borrower_id or "-",
            ]
            for column, value in enumerate(values):
                ctk.CTkLabel(row, text=value, anchor="w").grid(
                    row=0, column=column, sticky="ew", padx=8, pady=6
                )

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="CTkButton Warning: Given image is not CTkImage",
                    category=UserWarning,
                )
                delete_button = ctk.CTkButton(
                    row,
                    text="",
                    image=self._trash_icon,
                    width=40,
                    height=30,
                    fg_color="#b33939",
                    hover_color="#8f2c2c",
                    command=lambda isbn=book.isbn, titre=book.title: self.confirm_delete(
                        isbn, titre
                    ),
                )
            delete_button.grid(row=0, column=len(values), padx=8, pady=4)

        if books:
            self.rows.grid()
            self.empty_label.place_forget()
        else:
            self.rows.grid_remove()
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def confirm_delete(self, isbn, title):
        """Demande confirmation avant de supprimer un livre."""
        book = self.app.service.find_book_by_isbn(isbn)
        if book is None:
            self.app.show_error(f"Le livre avec l'ISBN {isbn} n'existe pas.")
            self.refresh()
            return

        if not book.is_available:
            message = (
                f"Le livre « {title} » est actuellement emprunté par "
                f"{book.borrower_id}.\n\nVoulez-vous vraiment le supprimer ?"
            )
            dialog_title = "Livre emprunté"
        else:
            message = f"Voulez-vous vraiment supprimer « {title} » ?"
            dialog_title = "Confirmation de suppression"

        if not messagebox.askyesno(dialog_title, message):
            return

        try:
            self.app.service.remove_book(isbn)
        except ServiceError as error:
            self.app.show_error(str(error))
            return

        self.app.mark_unsaved()
        self.app.show_success(f"Livre « {title} » supprimé.")
        self.refresh()

    def open_add_dialog(self):
        """Ouvre un dialog pour ajouter un nouveau livre."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajouter un livre")
        dialog.geometry("420x360")
        dialog.minsize(400, 320)
        dialog.transient(self.winfo_toplevel())
        dialog.grid_columnconfigure(1, weight=1)

        title_var = tk.StringVar()
        author_var = tk.StringVar()
        isbn_var = tk.StringVar()

        fields = [
            ("Titre :", title_var),
            ("Auteur :", author_var),
            ("ISBN :", isbn_var),
        ]
        for row, (label, variable) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).grid(
                row=row, column=0, sticky="w", padx=(20, 10), pady=10
            )
            ctk.CTkEntry(dialog, textvariable=variable).grid(
                row=row, column=1, sticky="ew", padx=(0, 20), pady=10
            )

        def add_book():
            title = title_var.get().strip()
            try:
                self.app.service.add_book(
                    title,
                    author_var.get().strip(),
                    isbn_var.get().strip(),
                )
            except ServiceError as error:
                self.app.show_error(str(error))
                return
            self.app.mark_unsaved()
            self.app.show_success(f"Livre '{title}' ajouté avec succès.")
            self.refresh()
            dialog.destroy()

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.grid(
            row=len(fields), column=0, columnspan=2, sticky="ew", padx=20, pady=20
        )
        buttons.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(buttons, text="Annuler", command=dialog.destroy).grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        ctk.CTkButton(buttons, text="Ajouter", command=add_book).grid(
            row=0, column=1, sticky="ew"
        )

        dialog.grab_set()
