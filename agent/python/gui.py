"""Interface graphique tkinter pour la bibliotheque C++ (bibliotheque_py)."""

import argparse
import shutil
import tempfile
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import bibliotheque_py as bp

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class LibraryController:
    """Couche logique : convertit les objets pybind11 en donnees Python simples."""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.library = bp.Library()
        self.files = None

    def load(self):
        if not self.data_dir.is_dir():
            raise ValueError(f"Dossier introuvable : {self.data_dir}")
        self.library = bp.Library()
        self.files = bp.FileManager(str(self.data_dir / "books.txt"),
                                    str(self.data_dir / "users.txt"))
        self.files.load_library_data(self.library)
        return self.stats()

    def save(self):
        self._require_files()
        return self.files.save_library_data(self.library)

    def backup(self):
        self._require_files()
        self.files.create_backup()

    def _require_files(self):
        if self.files is None:
            self.load()

    def add_book(self, title, author, isbn):
        if not (title and author and isbn):
            raise ValueError("Le titre, l'auteur et l'ISBN sont obligatoires.")
        if self.library.find_book_by_isbn(isbn) is not None:
            raise ValueError(f"Un livre avec l'ISBN {isbn} existe deja.")
        self.library.add_book(bp.Book(title, author, isbn))

    def remove_book(self, isbn):
        if not self.library.remove_book(isbn):
            raise ValueError("Livre introuvable.")

    def all_books(self):
        return [self._book_dict(book) for book in self.library.get_all_books()]

    def available_books(self):
        return [self._book_dict(book) for book in self.library.get_available_books()]

    def search_books(self, term, by="title"):
        if not term:
            return self.all_books()
        if by == "title":
            books = self.library.search_books_by_title(term)
        elif by == "author":
            books = self.library.search_books_by_author(term)
        else:
            raise ValueError("Recherche inconnue.")
        return [self._book_dict(book) for book in books]

    @staticmethod
    def _book_dict(book):
        return {
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "available": book.available,
            "borrower_id": book.borrower_id,
        }

    def add_user(self, name, user_id):
        if not (name and user_id):
            raise ValueError("Le nom et l'identifiant sont obligatoires.")
        if self.library.find_user_by_id(user_id) is not None:
            raise ValueError(f"Un utilisateur avec l'ID {user_id} existe deja.")
        self.library.add_user(bp.User(name, user_id))

    def all_users(self):
        return [{"name": user.name, "user_id": user.user_id,
                 "borrowed": user.borrowed_books}
                for user in self.library.get_all_users()]

    def check_out(self, isbn, user_id):
        if not self.library.check_out_book(isbn, user_id):
            raise ValueError("Emprunt impossible : verifiez ISBN, ID et disponibilite.")

    def return_book(self, isbn):
        if not self.library.return_book(isbn):
            raise ValueError("Retour impossible : verifiez l'ISBN.")

    def stats(self):
        return {
            "total": self.library.get_total_books(),
            "available": self.library.get_available_book_count(),
            "borrowed": self.library.get_checked_out_book_count(),
            "users": len(self.library.get_all_users()),
        }


class BibliothequeApp(tk.Tk):
    def __init__(self, data_dir):
        super().__init__()
        self.title("Gestion de bibliotheque")
        self.geometry("1020x650")
        self.controller = LibraryController(data_dir)
        self.data_var = tk.StringVar(value=str(data_dir))
        self.status_var = tk.StringVar(value="Pret.")
        self._configure_style()
        self._build_widgets()
        self._load(quiet=True)

    def _configure_style(self):
        self.colors = {
            "bg": "#f4f7fb",
            "panel": "#ffffff",
            "accent": "#2b6cb0",
            "accent_fg": "#ffffff",
            "text": "#1a202c",
            "muted": "#4a5568",
            "success": "#2f855a",
            "error": "#c53030",
            "warning": "#b7791f",
            "available": "#c6f6d5",
            "borrowed": "#fed7d7",
            "tree_alt": "#edf2f7",
        }
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(bg=self.colors["bg"])
        style.configure(".", background=self.colors["bg"], foreground=self.colors["text"], fieldbackground=self.colors["panel"])
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TLabelframe", background=self.colors["bg"])
        style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["accent"], font=("TkDefaultFont", 10, "bold"))
        style.configure("TNotebook", background=self.colors["bg"])
        style.configure("TNotebook.Tab", padding=(12, 6))
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", foreground=self.colors["accent_fg"], background=self.colors["accent"])
        style.map("Accent.TButton", background=[("active", "#245a94"), ("pressed", "#1e4e82")])
        style.configure("Treeview", background=self.colors["panel"], fieldbackground=self.colors["panel"], foreground=self.colors["text"], rowheight=24)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"))
        style.map("Treeview", background=[("selected", self.colors["accent"])], foreground=[("selected", "#ffffff")])
        style.configure("Status.TLabel", background="#e2e8f0", foreground=self.colors["muted"], padding=(10, 4))
        style.configure("StatusSuccess.TLabel", background="#c6f6d5", foreground=self.colors["success"], padding=(10, 4))
        style.configure("StatusError.TLabel", background="#fed7d7", foreground=self.colors["error"], padding=(10, 4))
        style.configure("StatusInfo.TLabel", background="#bee3f8", foreground=self.colors["accent"], padding=(10, 4))

    def _build_widgets(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Dossier de donnees :").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.data_var, width=55).grid(row=0, column=1, padx=5)
        ttk.Button(top, text="Parcourir...", command=self._choose_dir).grid(row=0, column=2, padx=3)
        ttk.Button(top, text="Charger", command=self._load).grid(row=0, column=3, padx=3)
        ttk.Button(top, text="Sauvegarder", command=self._save, style="Accent.TButton").grid(row=0, column=4, padx=3)
        ttk.Button(top, text="Creer une sauvegarde", command=self._backup).grid(row=0, column=5, padx=3)
        ttk.Label(top, foreground=self.colors["warning"],
                  text="Attention : la sauvegarde reecrit books.txt et users.txt (fichiers suivis par git)."
                  ).grid(row=1, column=1, columnspan=5, sticky="w", pady=(4, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        self._build_books_tab(notebook)
        self._build_users_tab(notebook)

        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor="w",
                                      style="Status.TLabel")
        self.status_label.pack(fill="x")

    def _build_books_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=8)
        notebook.add(tab, text="Livres")

        form = ttk.LabelFrame(tab, text="Ajouter / supprimer un livre", padding=8)
        form.pack(fill="x")
        self.title_var, self.author_var, self.isbn_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for col, (label, var) in enumerate((("Titre", self.title_var),
                                            ("Auteur", self.author_var),
                                            ("ISBN", self.isbn_var))):
            ttk.Label(form, text=label).grid(row=0, column=col * 2, sticky="w")
            ttk.Entry(form, textvariable=var, width=28).grid(row=0, column=col * 2 + 1, padx=(3, 12))
        ttk.Button(form, text="Ajouter", command=self._add_book, style="Accent.TButton").grid(row=1, column=0, pady=(8, 0))
        ttk.Button(form, text="Supprimer (ISBN)", command=self._remove_book).grid(row=1, column=2, pady=(8, 0))

        search = ttk.LabelFrame(tab, text="Recherche et filtres", padding=8)
        search.pack(fill="x", pady=(8, 0))
        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Titre")
        ttk.Entry(search, textvariable=self.search_var, width=35).grid(row=0, column=0)
        ttk.Combobox(search, textvariable=self.search_by_var, state="readonly",
                     values=("Titre", "Auteur"), width=10).grid(row=0, column=1, padx=5)
        ttk.Button(search, text="Rechercher", command=self._search, style="Accent.TButton").grid(row=0, column=2)
        ttk.Button(search, text="Tous les livres", command=self._refresh).grid(row=0, column=3, padx=5)
        ttk.Button(search, text="Disponibles", command=self._available).grid(row=0, column=4)

        container = ttk.Frame(tab)
        container.pack(fill="both", expand=True, pady=(8, 0))
        self.books_tree = ttk.Treeview(container,
                                       columns=("title", "author", "isbn", "available", "borrower"),
                                       show="headings")
        for key, label, width in (("title", "Titre", 260), ("author", "Auteur", 200),
                                  ("isbn", "ISBN", 150), ("available", "Disponible", 100),
                                  ("borrower", "Emprunteur", 120)):
            self.books_tree.heading(key, text=label)
            self.books_tree.column(key, width=width)
        self.books_tree.tag_configure("available", background=self.colors["available"])
        self.books_tree.tag_configure("borrowed", background=self.colors["borrowed"])
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        self.books_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_users_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=8)
        notebook.add(tab, text="Utilisateurs")

        form = ttk.LabelFrame(tab, text="Ajouter un utilisateur", padding=8)
        form.pack(fill="x")
        self.name_var, self.user_id_var = tk.StringVar(), tk.StringVar()
        ttk.Label(form, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=(3, 12))
        ttk.Label(form, text="ID").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.user_id_var, width=20).grid(row=0, column=3, padx=3)
        ttk.Button(form, text="Ajouter", command=self._add_user, style="Accent.TButton").grid(row=0, column=4, padx=12)

        loans = ttk.LabelFrame(tab, text="Emprunts", padding=8)
        loans.pack(fill="x", pady=(8, 0))
        self.loan_isbn_var, self.loan_user_var = tk.StringVar(), tk.StringVar()
        ttk.Label(loans, text="ISBN").grid(row=0, column=0, sticky="w")
        ttk.Entry(loans, textvariable=self.loan_isbn_var, width=24).grid(row=0, column=1, padx=(3, 12))
        ttk.Label(loans, text="ID utilisateur").grid(row=0, column=2, sticky="w")
        ttk.Entry(loans, textvariable=self.loan_user_var, width=20).grid(row=0, column=3, padx=3)
        ttk.Button(loans, text="Emprunter", command=self._check_out, style="Accent.TButton").grid(row=0, column=4, padx=(12, 3))
        ttk.Button(loans, text="Retourner", command=self._return_book).grid(row=0, column=5, padx=3)

        container = ttk.Frame(tab)
        container.pack(fill="both", expand=True, pady=(8, 0))
        self.users_tree = ttk.Treeview(container,
                                       columns=("name", "user_id", "borrowed"), show="headings")
        for key, label, width in (("name", "Nom", 250), ("user_id", "ID", 120),
                                  ("borrowed", "Livres empruntes", 450)):
            self.users_tree.heading(key, text=label)
            self.users_tree.column(key, width=width)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _status(self, message, kind="info"):
        self.status_var.set(message)
        if hasattr(self, "status_label"):
            styles = {
                "success": "StatusSuccess.TLabel",
                "error": "StatusError.TLabel",
                "info": "StatusInfo.TLabel",
                "neutral": "Status.TLabel",
            }
            self.status_label.configure(style=styles.get(kind, "StatusInfo.TLabel"))

    def _run(self, action, success):
        try:
            action()
        except (ValueError, OSError, RuntimeError) as error:
            self._status(f"Erreur : {error}", "error")
            messagebox.showerror("Erreur", str(error), parent=self)
            return False
        self._status(success, "success")
        return True

    def _fill_books(self, books):
        self.books_tree.delete(*self.books_tree.get_children())
        for book in books:
            tag = "available" if book["available"] else "borrowed"
            self.books_tree.insert("", "end", values=(
                book["title"], book["author"], book["isbn"],
                "Oui" if book["available"] else "Non", book["borrower_id"]), tags=(tag,))

    def _fill_users(self, users):
        self.users_tree.delete(*self.users_tree.get_children())
        for user in users:
            self.users_tree.insert("", "end", values=(
                user["name"], user["user_id"], ", ".join(user["borrowed"])))

    def _refresh(self):
        self._fill_books(self.controller.all_books())
        self._fill_users(self.controller.all_users())
        stats = self.controller.stats()
        self._status(f"Livres : {stats['total']} (disponibles : {stats['available']}, "
                     f"empruntes : {stats['borrowed']}) - Utilisateurs : {stats['users']}", "info")

    def _choose_dir(self):
        directory = filedialog.askdirectory(initialdir=self.data_var.get(), parent=self)
        if directory:
            self.data_var.set(directory)
            self._load()

    def _load(self, quiet=False):
        try:
            self.controller = LibraryController(self.data_var.get())
            self.controller.load()
            self._refresh()
        except (ValueError, OSError, RuntimeError) as error:
            if quiet:
                self._status(f"Chargement impossible : {error}", "error")
            else:
                self._status(f"Erreur : {error}", "error")
                messagebox.showerror("Erreur", str(error), parent=self)
            return
        self._status("Donnees chargees.", "success")

    def _save(self):
        self._run(self.controller.save, "Donnees sauvegardees.")

    def _backup(self):
        self._run(self.controller.backup, "Sauvegarde creee.")

    def _add_book(self):
        def action():
            self.controller.add_book(self.title_var.get().strip(),
                                     self.author_var.get().strip(),
                                     self.isbn_var.get().strip())
            self._refresh()
        if self._run(action, "Livre ajoute."):
            self.title_var.set("")
            self.author_var.set("")
            self.isbn_var.set("")

    def _remove_book(self):
        isbn = self.isbn_var.get().strip()
        if not isbn:
            self._status("Entrez un ISBN pour supprimer un livre.", "error")
            messagebox.showwarning("Suppression", "Entrez un ISBN.", parent=self)
            return
        if not messagebox.askyesno("Suppression", f"Supprimer le livre {isbn} ?", parent=self):
            return
        self._run(lambda: (self.controller.remove_book(isbn), self._refresh()), "Livre supprime.")

    def _search(self):
        by = "title" if self.search_by_var.get() == "Titre" else "author"
        books = self.controller.search_books(self.search_var.get().strip(), by)
        self._fill_books(books)
        self._status(f"{len(books)} resultat(s).", "info")

    def _available(self):
        books = self.controller.available_books()
        self._fill_books(books)
        self._status(f"{len(books)} livre(s) disponible(s).", "success" if books else "info")

    def _add_user(self):
        def action():
            self.controller.add_user(self.name_var.get().strip(),
                                     self.user_id_var.get().strip())
            self._refresh()
        if self._run(action, "Utilisateur ajoute."):
            self.name_var.set("")
            self.user_id_var.set("")

    def _check_out(self):
        def action():
            self.controller.check_out(self.loan_isbn_var.get().strip(),
                                      self.loan_user_var.get().strip())
            self._refresh()
        self._run(action, "Livre emprunte.")

    def _return_book(self):
        def action():
            self.controller.return_book(self.loan_isbn_var.get().strip())
            self._refresh()
        self._run(action, "Livre retourne.")


def selftest():
    """Teste la logique sans fenetre ni affichage graphique."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        shutil.copy(DEFAULT_DATA_DIR / "books.txt", tmp_dir / "books.txt")
        shutil.copy(DEFAULT_DATA_DIR / "users.txt", tmp_dir / "users.txt")

        controller = LibraryController(tmp_dir)
        controller.load()
        isbn = "9780000000001"
        controller.add_book("Un livre", "Un auteur", isbn)
        assert len(controller.search_books("Un livre")) == 1
        user_id = controller.all_users()[0]["user_id"]
        controller.check_out(isbn, user_id)
        book = next(book for book in controller.all_books() if book["isbn"] == isbn)
        assert not book["available"] and book["borrower_id"] == user_id
        controller.return_book(isbn)
        assert controller.save()
        print(f"Self-test OK : {controller.stats()}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Interface graphique de la bibliotheque C++")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR),
                        help="Dossier contenant books.txt et users.txt")
    parser.add_argument("--selftest", action="store_true",
                        help="Tester la logique sans ouvrir la fenetre")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
    else:
        BibliothequeApp(args.data_dir).mainloop()


if __name__ == "__main__":
    main()
