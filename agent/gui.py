import os
import sys
from tkinter import messagebox, ttk

import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "build")
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.insert(0, BUILD_DIR)

try:
    import bibliotheque_py
except ImportError as exc:
    print(
        "Impossible de charger le module 'bibliotheque_py'.\n"
        "Compilez-le avec : mkdir -p build && cd build && cmake .. && make",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


EMPTY_ROW = "__empty__"
COLUMN_TITLES = {
    "title": "Titre",
    "author": "Auteur",
    "isbn": "ISBN",
    "status": "Statut",
}


class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bibliothèque")
        self.geometry("1000x700")
        self.minsize(800, 560)

        self.library = bibliotheque_py.Library()
        self.file_manager = bibliotheque_py.FileManager(
            os.path.join(DATA_DIR, "books.txt"),
            os.path.join(DATA_DIR, "users.txt"),
        )

        self.title_var = ctk.StringVar()
        self.author_var = ctk.StringVar()
        self.isbn_var = ctk.StringVar()
        self.user_id_var = ctk.StringVar()
        self.search_var = ctk.StringVar()
        self.stats_var = ctk.StringVar(value="")
        self.status_var = ctk.StringVar(value="")

        self.sort_key = "title"
        self.sort_reverse = False

        self._build_ui()
        self._load_data()
        self._refresh_users()
        self.refresh_books()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        header = ctk.CTkLabel(
            self,
            text="Gestion de la bibliothèque",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure((1, 3), weight=1)

        self._add_field(form, "Titre", self.title_var, 0, 0)
        self._add_field(form, "Auteur", self.author_var, 0, 2)
        self._add_field(form, "ISBN", self.isbn_var, 1, 0)
        self._add_user_field(form, "Utilisateur", self.user_id_var, 1, 2)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkButton(actions, text="Ajouter un livre", command=self.add_book).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkButton(actions, text="Emprunter", command=self.borrow_book).pack(
            side="left", padx=10
        )
        ctk.CTkButton(actions, text="Retourner", command=self.return_book).pack(
            side="left", padx=10
        )
        ctk.CTkButton(
            actions, text="Supprimer", command=self.remove_book, fg_color="#8a3b3b"
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            actions, text="Ajouter un utilisateur", command=self.add_user
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            actions, text="Effacer", command=self.clear_form, fg_color="gray40"
        ).pack(side="left", padx=10)
        ctk.CTkButton(actions, text="Sauvegarder", command=self.save_data).pack(
            side="left", padx=10
        )

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        toolbar.grid_columnconfigure(0, weight=1)

        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="Rechercher par titre, auteur ou ISBN",
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_books())

        ctk.CTkLabel(
            toolbar, textvariable=self.stats_var, font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, sticky="e")

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=4, column=0, padx=20, pady=(10, 10), sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self._configure_tree_style()

        self.books_tree = ttk.Treeview(
            table_frame,
            columns=("title", "author", "isbn", "status"),
            show="headings",
            style="Books.Treeview",
            selectmode="browse",
        )
        self.books_tree.heading(
            "title", text="Titre", anchor="w", command=lambda: self._sort_by("title")
        )
        self.books_tree.heading(
            "author", text="Auteur", anchor="w", command=lambda: self._sort_by("author")
        )
        self.books_tree.heading(
            "isbn", text="ISBN", anchor="w", command=lambda: self._sort_by("isbn")
        )
        self.books_tree.heading(
            "status", text="Statut", anchor="w", command=lambda: self._sort_by("status")
        )
        self.books_tree.column("title", width=320, minwidth=160, stretch=True, anchor="w")
        self.books_tree.column("author", width=220, minwidth=140, stretch=True, anchor="w")
        self.books_tree.column("isbn", width=170, minwidth=130, stretch=False, anchor="w")
        self.books_tree.column("status", width=190, minwidth=170, stretch=False, anchor="w")
        self.books_tree.grid(row=0, column=0, sticky="nsew")
        for tag, options in self.books_tree_tags.items():
            self.books_tree.tag_configure(tag, **options)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.books_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.books_tree.configure(yscrollcommand=scrollbar.set)

        self.books_tree.bind("<<TreeviewSelect>>", self._on_select)
        self.books_tree.bind("<Double-1>", self._on_double_click)

        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w")
        self.status_label.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="ew")

    def _configure_tree_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        dark = ctk.get_appearance_mode() == "Dark"
        background = "#242424" if dark else "#ffffff"
        stripe = "#2f2f2f" if dark else "#f2f2f2"
        foreground = "#dce4ee" if dark else "#1a1a1a"
        heading_bg = "#1f1f1f" if dark else "#e5e5e5"
        selected = "#1f6aa5"

        style.configure(
            "Books.Treeview",
            background=background,
            fieldbackground=background,
            foreground=foreground,
            rowheight=30,
            borderwidth=0,
            font=("TkDefaultFont", 11),
        )
        style.configure(
            "Books.Treeview.Heading",
            background=heading_bg,
            foreground=foreground,
            font=("TkDefaultFont", 11, "bold"),
            relief="flat",
            padding=(8, 6),
        )
        style.map(
            "Books.Treeview",
            background=[("selected", selected)],
            foreground=[("selected", "#ffffff")],
        )
        style.map("Books.Treeview.Heading", background=[("active", "#2a5f86")])

        self.books_tree_tags = {
            "pair": {"background": stripe},
            "impair": {"background": background},
            "dispo": {"foreground": "#2fa572"},
            "emprunte": {"foreground": "#d9534f"},
        }

    def _add_field(self, parent, label, variable, row, column):
        ctk.CTkLabel(parent, text=label).grid(
            row=row, column=column, padx=(10, 5), pady=8, sticky="e"
        )
        ctk.CTkEntry(parent, textvariable=variable).grid(
            row=row, column=column + 1, padx=(5, 10), pady=8, sticky="ew"
        )

    def _add_user_field(self, parent, label, variable, row, column):
        ctk.CTkLabel(parent, text=label).grid(
            row=row, column=column, padx=(10, 5), pady=8, sticky="e"
        )
        self.user_combo = ctk.CTkComboBox(parent, variable=variable, values=[""])
        self.user_combo.grid(
            row=row, column=column + 1, padx=(5, 10), pady=8, sticky="ew"
        )

    def _load_data(self):
        try:
            self.file_manager.loadLibraryData(self.library)
            self._set_status("Données chargées.", success=True)
        except Exception as error:
            self._set_status(f"Erreur de chargement : {error}", success=False)

    def _refresh_users(self):
        values = [
            f"{user.getUserId()} | {user.getName()}"
            for user in self.library.getAllUsers()
        ]
        self.user_combo.configure(values=values or [""])

    def _selected_user_id(self):
        raw = self.user_id_var.get().strip()
        if "|" in raw:
            raw = raw.split("|", 1)[0].strip()
        return raw

    def _sort_by(self, key):
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = False
        self._update_headings()
        self.refresh_books()

    def _update_headings(self):
        for key, title in COLUMN_TITLES.items():
            suffix = ""
            if key == self.sort_key:
                suffix = " ▼" if self.sort_reverse else " ▲"
            self.books_tree.heading(key, text=title + suffix, anchor="w")

    def _book_sort_value(self, book):
        if self.sort_key == "title":
            return book.getTitle().lower()
        if self.sort_key == "author":
            return book.getAuthor().lower()
        if self.sort_key == "isbn":
            return book.getISBN()
        return book.getAvailability()

    def refresh_books(self):
        selected = self.books_tree.selection()
        selected_isbn = selected[0] if selected else None
        scroll_position = self.books_tree.yview()[0]

        self.books_tree.delete(*self.books_tree.get_children())
        self._update_headings()

        query = self.search_var.get().strip().lower()
        books = []
        for book in self.library.getAllBooks():
            title = book.getTitle()
            author = book.getAuthor()
            isbn = book.getISBN()
            if query and not (
                query in title.lower()
                or query in author.lower()
                or query in isbn.lower()
            ):
                continue
            books.append(book)

        books.sort(key=self._book_sort_value, reverse=self.sort_reverse)

        if not books:
            self.books_tree.insert(
                "", "end", iid=EMPTY_ROW,
                values=("Aucun livre trouvé.", "", "", ""),
            )
        else:
            for row, book in enumerate(books):
                available = book.getAvailability()
                status = (
                    "Disponible"
                    if available
                    else f"Emprunté ({book.getBorrowerId()})"
                )
                tags = ("pair" if row % 2 == 0 else "impair",)
                tags += ("dispo",) if available else ("emprunte",)
                self.books_tree.insert(
                    "",
                    "end",
                    iid=book.getISBN(),
                    values=(book.getTitle(), book.getAuthor(), book.getISBN(), status),
                    tags=tags,
                )

        self._update_stats()

        if selected_isbn and self.books_tree.exists(selected_isbn):
            self.books_tree.selection_set(selected_isbn)
            self.books_tree.focus(selected_isbn)
        self.books_tree.yview_moveto(scroll_position)

    def _update_stats(self):
        self.stats_var.set(
            f"Total : {self.library.getTotalBooks()}   •   "
            f"Disponibles : {self.library.getAvailableBookCount()}   •   "
            f"Empruntés : {self.library.getCheckedOutBookCount()}"
        )

    def _on_select(self, _event=None):
        selection = self.books_tree.selection()
        if not selection or selection[0] == EMPTY_ROW:
            return
        isbn = selection[0]
        book = self.library.findBookByISBN(isbn)
        if book is None:
            return
        self.isbn_var.set(isbn)
        if not book.getAvailability():
            self.user_id_var.set(book.getBorrowerId())

    def _on_double_click(self, event):
        row_id = self.books_tree.identify_row(event.y)
        if not row_id or row_id == EMPTY_ROW:
            return
        self.isbn_var.set(row_id)
        book = self.library.findBookByISBN(row_id)
        if book is None:
            return
        if book.getAvailability():
            self.borrow_book()
        else:
            self.return_book()

    def add_book(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        isbn = self.isbn_var.get().strip()

        if not title or not author or not isbn:
            self._set_status("Titre, auteur et ISBN sont obligatoires.", success=False)
            return

        if self.library.findBookByISBN(isbn) is not None:
            self._set_status("Un livre avec cet ISBN existe déjà.", success=False)
            return

        try:
            book = bibliotheque_py.Book(title, author, isbn)
            self.library.addBook(book)
            self.title_var.set("")
            self.author_var.set("")
            self.isbn_var.set("")
            self.refresh_books()
            self._set_status(f"Livre « {title} » ajouté.", success=True)
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def add_user(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajouter un utilisateur")
        dialog.geometry("380x220")
        dialog.transient(self)
        dialog.grab_set()

        name_var = ctk.StringVar()
        new_id_var = ctk.StringVar()

        ctk.CTkLabel(dialog, text="Nom").grid(
            row=0, column=0, padx=(15, 5), pady=(20, 8), sticky="e"
        )
        ctk.CTkEntry(dialog, textvariable=name_var).grid(
            row=0, column=1, padx=(5, 15), pady=(20, 8), sticky="ew"
        )
        ctk.CTkLabel(dialog, text="ID").grid(
            row=1, column=0, padx=(15, 5), pady=8, sticky="e"
        )
        ctk.CTkEntry(dialog, textvariable=new_id_var).grid(
            row=1, column=1, padx=(5, 15), pady=8, sticky="ew"
        )
        dialog.grid_columnconfigure(1, weight=1)

        def create_user():
            name = name_var.get().strip()
            user_id = new_id_var.get().strip()
            if not name or not user_id:
                messagebox.showwarning(
                    "Champs requis",
                    "Le nom et l'ID sont obligatoires.",
                    parent=dialog,
                )
                return
            if self.library.findUserById(user_id) is not None:
                messagebox.showwarning(
                    "ID déjà utilisé",
                    f"Un utilisateur avec l'ID {user_id} existe déjà.",
                    parent=dialog,
                )
                return
            try:
                self.library.addUser(bibliotheque_py.User(name, user_id))
            except Exception as error:
                messagebox.showerror("Erreur", str(error), parent=dialog)
                return
            self._refresh_users()
            self.user_id_var.set(f"{user_id} | {name}")
            self._set_status(f"Utilisateur « {name} » ajouté.", success=True)
            dialog.destroy()

        ctk.CTkButton(dialog, text="Ajouter", command=create_user).grid(
            row=2, column=0, columnspan=2, padx=15, pady=(15, 15), sticky="ew"
        )

    def borrow_book(self):
        isbn = self.isbn_var.get().strip()
        user_id = self._selected_user_id()

        if not isbn or not user_id:
            self._set_status(
                "ISBN et utilisateur sont obligatoires.", success=False
            )
            return

        try:
            if self.library.checkOutBook(isbn, user_id):
                self.refresh_books()
                self._set_status(f"Livre {isbn} emprunté par {user_id}.", success=True)
            else:
                self._set_status(
                    "Emprunt impossible : livre indisponible, ISBN ou utilisateur inconnu.",
                    success=False,
                )
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def return_book(self):
        isbn = self.isbn_var.get().strip()

        if not isbn:
            self._set_status("L'ISBN est obligatoire.", success=False)
            return

        try:
            if self.library.returnBook(isbn):
                self.refresh_books()
                self._set_status(f"Livre {isbn} retourné.", success=True)
            else:
                self._set_status(
                    "Retour impossible : livre inconnu ou déjà disponible.",
                    success=False,
                )
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def remove_book(self):
        isbn = self.isbn_var.get().strip()
        if not isbn:
            selection = self.books_tree.selection()
            if selection and selection[0] != EMPTY_ROW:
                isbn = selection[0]

        if not isbn:
            self._set_status("Sélectionnez un livre à supprimer.", success=False)
            return

        book = self.library.findBookByISBN(isbn)
        if book is None:
            self._set_status("Livre inconnu.", success=False)
            return

        if not messagebox.askyesno(
            "Supprimer le livre",
            f"Supprimer « {book.getTitle()} » (ISBN {isbn}) ?",
            parent=self,
        ):
            return

        try:
            if self.library.removeBook(isbn):
                if self.isbn_var.get().strip() == isbn:
                    self.isbn_var.set("")
                self.refresh_books()
                self._set_status(f"Livre {isbn} supprimé.", success=True)
            else:
                self._set_status("Suppression impossible : livre inconnu.", success=False)
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def clear_form(self):
        self.title_var.set("")
        self.author_var.set("")
        self.isbn_var.set("")
        self.user_id_var.set("")
        selection = self.books_tree.selection()
        if selection:
            self.books_tree.selection_remove(*selection)
        self._set_status("Formulaire effacé.", success=True)

    def save_data(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            if self.file_manager.saveLibraryData(self.library):
                self._set_status("Données sauvegardées.", success=True)
            else:
                self._set_status("La sauvegarde a échoué.", success=False)
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def _set_status(self, message, success):
        self.status_var.set(message)
        self.status_label.configure(text_color="#2fa572" if success else "#d9534f")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = LibraryApp()
    app.mainloop()
