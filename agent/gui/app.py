"""Interface graphique customtkinter pour la bibliotheque personnelle.

Toute la logique metier reste dans les classes C++ exposees par
``bibliotheque_py``. Ce module se contente de collecter les saisies, d'appeler
les methodes C++ puis d'afficher les donnees renvoyees.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

try:
    import bibliotheque_py as biblio
except ImportError as exc:  # pragma: no cover - message d'aide a l'utilisateur
    raise SystemExit(
        "Module Python 'bibliotheque_py' introuvable.\n"
        "Compilez le projet puis lancez l'application avec :\n"
        "  PYTHONPATH=agent/build/python python agent/gui/app.py --data-dir agent/data"
    ) from exc


DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
NO_USER = "Aucun utilisateur"


class BibliothequeApp(ctk.CTk):
    def __init__(self, data_dir: str | Path) -> None:
        super().__init__()

        self.data_dir = Path(data_dir).expanduser().resolve()
        self.library = biblio.Library()
        self.file_manager = biblio.FileManager(
            str(self.data_dir / "books.txt"),
            str(self.data_dir / "users.txt"),
        )
        self.loaded = self.file_manager.load_library_data(self.library)

        self.title("Systeme de gestion de bibliotheque personnelle")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._configure_tree_style()
        self._build_layout()
        self._refresh_all()

        if self.loaded:
            self._set_status(f"Donnees chargees depuis {self.data_dir}")
        else:
            self._set_status("Aucun fichier de donnees trouve : bibliotheque vide.")

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _configure_tree_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#242424",
            fieldbackground="#242424",
            foreground="#f2f2f2",
            rowheight=26,
        )
        style.configure(
            "Treeview.Heading",
            background="#333333",
            foreground="#ffffff",
            font=("DejaVu Sans", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#1f6aa5")])

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="Systeme de gestion de bibliotheque personnelle",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 2))
        self.stats_label = ctk.CTkLabel(header, text="", anchor="w")
        self.stats_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.tab_books = self.tabview.add("Livres")
        self.tab_users = self.tabview.add("Utilisateurs")
        self.tab_loans = self.tabview.add("Emprunts")
        self.tab_data = self.tabview.add("Donnees")

        self._build_books_tab()
        self._build_users_tab()
        self._build_loans_tab()
        self._build_data_tab()

        self.status_var = tk.StringVar(value="Pret")
        ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            anchor="w",
            text_color=("#444444", "#c8c8c8"),
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

    def _build_books_tab(self) -> None:
        tab = self.tab_books
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        search = ctk.CTkFrame(tab)
        search.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        search.grid_columnconfigure(1, weight=1)

        self.title_search = ctk.CTkEntry(
            search, placeholder_text="Rechercher un titre", width=260
        )
        self.title_search.grid(row=0, column=0, sticky="w", padx=(8, 6), pady=(8, 4))
        ctk.CTkButton(
            search, text="Rechercher par titre", width=170, command=self._search_by_title
        ).grid(row=0, column=1, sticky="w", padx=6, pady=(8, 4))
        ctk.CTkButton(
            search, text="Tous les livres", width=130, command=self._show_all_books
        ).grid(row=0, column=3, padx=6, pady=(8, 4))

        self.author_search = ctk.CTkEntry(
            search, placeholder_text="Rechercher un auteur", width=260
        )
        self.author_search.grid(row=1, column=0, sticky="w", padx=(8, 6), pady=(4, 8))
        ctk.CTkButton(
            search,
            text="Rechercher par auteur",
            width=170,
            command=self._search_by_author,
        ).grid(row=1, column=1, sticky="w", padx=6, pady=(4, 8))
        ctk.CTkButton(
            search,
            text="Livres disponibles",
            width=130,
            command=self._show_available_books,
        ).grid(row=1, column=3, padx=6, pady=(4, 8))

        tree_frame = ctk.CTkFrame(tab)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("title", "author", "isbn", "status", "borrower")
        self.books_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )
        headings = {
            "title": ("Titre", 280),
            "author": ("Auteur", 220),
            "isbn": ("ISBN", 160),
            "status": ("Statut", 110),
            "borrower": ("Emprunteur", 130),
        }
        for column, (label, width) in headings.items():
            self.books_tree.heading(column, text=label)
            self.books_tree.column(column, width=width, anchor="w", stretch=True)
        self.books_tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        books_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.books_tree.yview
        )
        books_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.books_tree.configure(yscrollcommand=books_scrollbar.set)

        add_frame = ctk.CTkFrame(tab)
        add_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        add_frame.grid_columnconfigure(1, weight=1)
        add_frame.grid_columnconfigure(3, weight=1)
        add_frame.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(add_frame, text="Titre").grid(
            row=0, column=0, sticky="w", padx=(8, 4), pady=8
        )
        self.new_title = ctk.CTkEntry(add_frame, placeholder_text="Titre du livre")
        self.new_title.grid(row=0, column=1, sticky="ew", padx=4, pady=8)

        ctk.CTkLabel(add_frame, text="Auteur").grid(
            row=0, column=2, sticky="w", padx=(12, 4), pady=8
        )
        self.new_author = ctk.CTkEntry(add_frame, placeholder_text="Auteur")
        self.new_author.grid(row=0, column=3, sticky="ew", padx=4, pady=8)

        ctk.CTkLabel(add_frame, text="ISBN").grid(
            row=0, column=4, sticky="w", padx=(12, 4), pady=8
        )
        self.new_isbn = ctk.CTkEntry(add_frame, placeholder_text="ISBN")
        self.new_isbn.grid(row=0, column=5, sticky="ew", padx=4, pady=8)

        ctk.CTkButton(
            add_frame, text="Ajouter le livre", width=140, command=self._add_book
        ).grid(row=0, column=6, padx=(12, 8), pady=8)

        actions = ctk.CTkFrame(tab, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        ctk.CTkButton(
            actions,
            text="Supprimer le livre selectionne",
            width=240,
            fg_color="#8b2e2e",
            hover_color="#a13a3a",
            command=self._remove_selected_book,
        ).grid(row=0, column=0, padx=8, pady=4, sticky="w")
        ctk.CTkLabel(
            actions,
            text="Selectionnez une ligne dans le tableau pour la supprimer.",
            anchor="w",
        ).grid(row=0, column=1, padx=8, sticky="w")

    def _build_users_tab(self) -> None:
        tab = self.tab_users
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        tree_frame = ctk.CTkFrame(tab)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("name", "user_id", "borrowed")
        self.users_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )
        headings = {
            "name": ("Nom", 360),
            "user_id": ("Identifiant", 260),
            "borrowed": ("Livres empruntes", 180),
        }
        for column, (label, width) in headings.items():
            self.users_tree.heading(column, text=label)
            self.users_tree.column(column, width=width, anchor="w", stretch=True)
        self.users_tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        users_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.users_tree.yview
        )
        users_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)

        add_frame = ctk.CTkFrame(tab)
        add_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))
        add_frame.grid_columnconfigure(1, weight=1)
        add_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(add_frame, text="Nom").grid(
            row=0, column=0, sticky="w", padx=(8, 4), pady=8
        )
        self.new_user_name = ctk.CTkEntry(add_frame, placeholder_text="Nom de l'utilisateur")
        self.new_user_name.grid(row=0, column=1, sticky="ew", padx=4, pady=8)

        ctk.CTkLabel(add_frame, text="Identifiant").grid(
            row=0, column=2, sticky="w", padx=(12, 4), pady=8
        )
        self.new_user_id = ctk.CTkEntry(add_frame, placeholder_text="Identifiant unique")
        self.new_user_id.grid(row=0, column=3, sticky="ew", padx=4, pady=8)

        ctk.CTkButton(
            add_frame, text="Ajouter l'utilisateur", width=180, command=self._add_user
        ).grid(row=0, column=4, padx=(12, 8), pady=8)

    def _build_loans_tab(self) -> None:
        tab = self.tab_loans
        tab.grid_columnconfigure(0, weight=1)

        borrow_frame = ctk.CTkFrame(tab)
        borrow_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        borrow_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            borrow_frame,
            text="Emprunter un livre",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=5, sticky="w", padx=8, pady=(10, 4))

        ctk.CTkLabel(borrow_frame, text="ISBN").grid(
            row=1, column=0, sticky="w", padx=(8, 4), pady=(4, 10)
        )
        self.borrow_isbn = ctk.CTkEntry(borrow_frame, placeholder_text="ISBN du livre")
        self.borrow_isbn.grid(row=1, column=1, sticky="ew", padx=4, pady=(4, 10))

        ctk.CTkLabel(borrow_frame, text="Utilisateur").grid(
            row=1, column=2, sticky="w", padx=(12, 4), pady=(4, 10)
        )
        self.user_menu = ctk.CTkOptionMenu(
            borrow_frame, values=[NO_USER], width=240
        )
        self.user_menu.grid(row=1, column=3, sticky="w", padx=4, pady=(4, 10))
        ctk.CTkButton(
            borrow_frame, text="Emprunter", width=130, command=self._borrow_book
        ).grid(row=1, column=4, padx=(12, 8), pady=(4, 10))

        return_frame = ctk.CTkFrame(tab)
        return_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        return_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            return_frame,
            text="Retourner un livre",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(10, 4))

        ctk.CTkLabel(return_frame, text="ISBN").grid(
            row=1, column=0, sticky="w", padx=(8, 4), pady=(4, 10)
        )
        self.return_isbn = ctk.CTkEntry(return_frame, placeholder_text="ISBN du livre")
        self.return_isbn.grid(row=1, column=1, sticky="ew", padx=4, pady=(4, 10))
        ctk.CTkButton(
            return_frame, text="Retourner", width=130, command=self._return_book
        ).grid(row=1, column=2, padx=(12, 8), pady=(4, 10))

        ctk.CTkLabel(
            tab,
            text=(
                "Les emprunts et retours sont valides par le code C++ : un ISBN "
                "inconnu, un utilisateur inconnu ou un livre deja emprunte est refuse."
            ),
            justify="left",
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(8, 8))

    def _build_data_tab(self) -> None:
        tab = self.tab_data
        tab.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(tab)
        info.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        info.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            info,
            text="Fichiers de donnees",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(10, 4))
        ctk.CTkLabel(info, text="Repertoire :", anchor="w").grid(
            row=1, column=0, sticky="w", padx=(8, 4), pady=4
        )
        ctk.CTkLabel(info, text=str(self.data_dir), anchor="w").grid(
            row=1, column=1, sticky="w", padx=4, pady=4
        )
        ctk.CTkLabel(
            info,
            text=(
                "Les modifications sont ecrites dans books.txt et users.txt "
                "uniquement lorsque vous cliquez sur Sauvegarder (ou a la fermeture)."
            ),
            justify="left",
            anchor="w",
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 10))

        actions = ctk.CTkFrame(tab)
        actions.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        ctk.CTkButton(
            actions, text="Sauvegarder les donnees", width=190, command=self._save_data
        ).grid(row=0, column=0, padx=8, pady=10, sticky="w")
        ctk.CTkButton(
            actions, text="Creer une sauvegarde", width=190, command=self._create_backup
        ).grid(row=0, column=1, padx=8, pady=10, sticky="w")
        ctk.CTkLabel(
            actions,
            text="La sauvegarde cree books.txt.backup et users.txt.backup.",
            anchor="w",
        ).grid(row=0, column=2, padx=8, sticky="w")

    # ------------------------------------------------------------------
    # Rafraichissement depuis le C++
    # ------------------------------------------------------------------
    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _refresh_all(self) -> None:
        self._refresh_stats()
        self._refresh_books()
        self._refresh_users()
        self._refresh_user_menu()

    def _refresh_stats(self) -> None:
        self.stats_label.configure(
            text=(
                f"Livres : {self.library.get_total_books()}   |   "
                f"Disponibles : {self.library.get_available_book_count()}   |   "
                f"Empruntes : {self.library.get_checked_out_book_count()}   |   "
                f"Utilisateurs : {len(self.library.get_all_users())}"
            )
        )

    def _refresh_books(self, books: list[biblio.Book] | None = None) -> None:
        if books is None:
            books = self.library.get_all_books()
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        for book in books:
            status = "Disponible" if book.is_available else "Emprunte"
            borrower = book.borrower_id if book.borrower_id else "-"
            self.books_tree.insert(
                "",
                "end",
                values=(book.title, book.author, book.isbn, status, borrower),
            )

    def _refresh_users(self) -> None:
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        for user in self.library.get_all_users():
            self.users_tree.insert(
                "",
                "end",
                values=(user.name, user.user_id, user.number_of_borrowed_books),
            )

    def _refresh_user_menu(self) -> None:
        user_ids = [user.user_id for user in self.library.get_all_users()]
        values = user_ids if user_ids else [NO_USER]
        current = self.user_menu.get()
        self.user_menu.configure(values=values)
        self.user_menu.set(current if current in values else values[0])

    def _selected_isbn(self) -> str | None:
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aucune selection", "Selectionnez d'abord un livre dans le tableau."
            )
            return None
        values = self.books_tree.item(selection[0], "values")
        return str(values[2])

    # ------------------------------------------------------------------
    # Actions livres
    # ------------------------------------------------------------------
    def _add_book(self) -> None:
        title = self.new_title.get().strip()
        author = self.new_author.get().strip()
        isbn = self.new_isbn.get().strip()
        if not title or not author or not isbn:
            messagebox.showwarning(
                "Champs incomplets", "Le titre, l'auteur et l'ISBN sont obligatoires."
            )
            return

        try:
            if self.library.book_exists(isbn):
                messagebox.showwarning(
                    "Livre existant", f"Un livre avec l'ISBN {isbn} existe deja."
                )
                return
            self.library.add_book(biblio.Book(title, author, isbn))
        except RuntimeError as exc:
            messagebox.showerror("Ajout impossible", str(exc))
            return

        self.new_title.delete(0, "end")
        self.new_author.delete(0, "end")
        self.new_isbn.delete(0, "end")
        self._refresh_all()
        self._set_status(f"Livre ajoute : {title}")

    def _remove_selected_book(self) -> None:
        isbn = self._selected_isbn()
        if isbn is None:
            return

        book = next(
            (item for item in self.library.get_all_books() if item.isbn == isbn), None
        )
        if book is not None and not book.is_available:
            proceed = messagebox.askyesno(
                "Livre emprunte",
                "Ce livre est actuellement emprunte. Le supprimer laissera "
                "l'historique de l'utilisateur inchange. Continuer ?",
            )
            if not proceed:
                return

        if not messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer le livre d'ISBN {isbn} ?",
        ):
            return

        try:
            removed = self.library.remove_book(isbn)
        except RuntimeError as exc:
            messagebox.showerror("Suppression impossible", str(exc))
            return

        if not removed:
            messagebox.showerror("Suppression impossible", "Livre introuvable.")
            return
        self._refresh_all()
        self._set_status(f"Livre supprime : {isbn}")

    def _search_by_title(self) -> None:
        query = self.title_search.get().strip()
        if not query:
            messagebox.showwarning("Recherche vide", "Saisissez un titre a rechercher.")
            return
        results = self.library.search_books_by_title(query)
        self._refresh_books(results)
        self._set_status(f"{len(results)} resultat(s) pour le titre « {query} ».")

    def _search_by_author(self) -> None:
        query = self.author_search.get().strip()
        if not query:
            messagebox.showwarning("Recherche vide", "Saisissez un auteur a rechercher.")
            return
        results = self.library.search_books_by_author(query)
        self._refresh_books(results)
        self._set_status(f"{len(results)} resultat(s) pour l'auteur « {query} ».")

    def _show_all_books(self) -> None:
        self._refresh_books()
        self._set_status("Tous les livres sont affiches.")

    def _show_available_books(self) -> None:
        books = self.library.get_available_books()
        self._refresh_books(books)
        self._set_status(f"{len(books)} livre(s) disponible(s).")

    # ------------------------------------------------------------------
    # Actions utilisateurs
    # ------------------------------------------------------------------
    def _add_user(self) -> None:
        name = self.new_user_name.get().strip()
        user_id = self.new_user_id.get().strip()
        if not name or not user_id:
            messagebox.showwarning(
                "Champs incomplets", "Le nom et l'identifiant sont obligatoires."
            )
            return

        try:
            if self.library.user_exists(user_id):
                messagebox.showwarning(
                    "Utilisateur existant",
                    f"Un utilisateur avec l'identifiant {user_id} existe deja.",
                )
                return
            self.library.add_user(biblio.User(name, user_id))
        except RuntimeError as exc:
            messagebox.showerror("Ajout impossible", str(exc))
            return

        self.new_user_name.delete(0, "end")
        self.new_user_id.delete(0, "end")
        self._refresh_all()
        self._set_status(f"Utilisateur ajoute : {name} ({user_id})")

    # ------------------------------------------------------------------
    # Actions emprunts
    # ------------------------------------------------------------------
    def _borrow_book(self) -> None:
        isbn = self.borrow_isbn.get().strip()
        user_id = self.user_menu.get()
        if not isbn:
            messagebox.showwarning("Champ vide", "Saisissez l'ISBN du livre.")
            return
        if user_id == NO_USER:
            messagebox.showwarning(
                "Aucun utilisateur", "Ajoutez d'abord un utilisateur."
            )
            return

        try:
            borrowed = self.library.check_out_book(isbn, user_id)
        except RuntimeError as exc:
            messagebox.showerror("Emprunt impossible", str(exc))
            return

        if not borrowed:
            messagebox.showerror(
                "Emprunt impossible",
                "Verifiez l'ISBN, l'utilisateur et la disponibilite du livre.",
            )
            return

        self.borrow_isbn.delete(0, "end")
        self._refresh_all()
        self._set_status(f"Livre {isbn} emprunte par {user_id}.")

    def _return_book(self) -> None:
        isbn = self.return_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Champ vide", "Saisissez l'ISBN du livre.")
            return

        try:
            returned = self.library.return_book(isbn)
        except RuntimeError as exc:
            messagebox.showerror("Retour impossible", str(exc))
            return

        if not returned:
            messagebox.showerror(
                "Retour impossible",
                "Verifiez l'ISBN et que le livre est bien emprunte.",
            )
            return

        self.return_isbn.delete(0, "end")
        self._refresh_all()
        self._set_status(f"Livre {isbn} retourne.")

    # ------------------------------------------------------------------
    # Sauvegarde et fermeture
    # ------------------------------------------------------------------
    def _save_data(self) -> bool:
        try:
            saved = self.file_manager.save_library_data(self.library)
        except RuntimeError as exc:
            messagebox.showerror("Sauvegarde impossible", str(exc))
            return False

        if not saved:
            messagebox.showerror(
                "Sauvegarde impossible",
                f"Impossible d'ecrire dans {self.data_dir}.",
            )
            return False
        self._set_status(f"Donnees sauvegardees dans {self.data_dir}")
        return True

    def _create_backup(self) -> None:
        try:
            self.file_manager.create_backup()
        except RuntimeError as exc:
            messagebox.showerror("Sauvegarde impossible", str(exc))
            return
        self._set_status("Fichiers de sauvegarde .backup crees.")

    def _on_close(self) -> None:
        answer = messagebox.askyesnocancel(
            "Quitter",
            "Enregistrer les donnees avant de quitter ?",
        )
        if answer is None:
            return
        if answer and not self._save_data():
            return
        self.destroy()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interface graphique de la bibliotheque personnelle"
    )
    parser.add_argument(
        "--data-dir",
        "-d",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Repertoire contenant books.txt et users.txt (defaut : agent/data)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = args.data_dir.expanduser().resolve()
    if not data_dir.is_dir():
        print(f"Erreur : le repertoire {data_dir} n'existe pas.")
        return 1

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = BibliothequeApp(data_dir)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
