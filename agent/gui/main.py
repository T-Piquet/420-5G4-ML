"""Interface graphique du système de gestion de bibliothèque personnelle."""

import argparse
import ctypes
import os
import queue
import re
import sys
import threading
from pathlib import Path
from tkinter import TclError, ttk

import customtkinter as ctk

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "build"))

try:
    import bibliotheque_core as core
except ImportError as exc:
    print(
        "Erreur : impossible d'importer le module bibliotheque_core.\n"
        "Compilez d'abord le projet : cmake -S agent -B agent/build "
        "&& cmake --build agent/build",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

MENU_GROUPS = [
    (
        "Livres",
        [
            (1, "Ajouter un Livre"),
            (2, "Supprimer un Livre"),
            (3, "Rechercher des Livres par Titre"),
            (4, "Rechercher des Livres par Auteur"),
            (5, "Afficher Tous les Livres"),
            (6, "Afficher les Livres Disponibles"),
        ],
    ),
    (
        "Utilisateurs",
        [
            (7, "Ajouter un Utilisateur"),
            (8, "Afficher Tous les Utilisateurs"),
        ],
    ),
    (
        "Opérations",
        [
            (9, "Emprunter un Livre"),
            (10, "Retourner un Livre"),
        ],
    ),
    (
        "Système",
        [
            (11, "Statistiques de la Bibliothèque"),
            (12, "Sauvegarder les Données"),
            (13, "Créer une Sauvegarde"),
        ],
    ),
]

_libc = ctypes.CDLL(None)


class JournalCpp:
    """Capture la sortie standard du processus, y compris les messages C++."""

    def __init__(self):
        self._lines: "queue.Queue[str]" = queue.Queue()
        self._original_fd = os.dup(1)
        sys.stdout.flush()
        read_fd, write_fd = os.pipe()
        os.dup2(write_fd, 1)
        os.close(write_fd)
        self._reader = threading.Thread(target=self._read, args=(read_fd,), daemon=True)
        self._reader.start()

    def _read(self, read_fd):
        with os.fdopen(read_fd, "r", encoding="utf-8", errors="replace") as stream:
            for line in stream:
                self._lines.put(line.rstrip("\n"))

    @staticmethod
    def flush():
        sys.stdout.flush()
        _libc.fflush(None)

    def drain(self):
        lines = []
        while True:
            try:
                lines.append(self._lines.get_nowait())
            except queue.Empty:
                break
        return lines

    def restore(self):
        sys.stdout.flush()
        try:
            os.dup2(self._original_fd, 1)
        finally:
            os.close(self._original_fd)


class FormDialog(ctk.CTkToplevel):
    """Boîte de dialogue modale avec plusieurs champs de saisie."""

    def __init__(self, master, title, fields, presets=None):
        super().__init__(master)
        self._fields = fields
        self._presets = presets or {}
        self._entries = []
        self._result = None
        self.title(title)
        self.resizable(False, False)
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Return>", lambda event: self._ok())
        self.bind("<Escape>", lambda event: self._cancel())
        self.after(10, self._build)

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        row = 0
        for index, label in enumerate(self._fields):
            ctk.CTkLabel(self, text=label, anchor="w").grid(
                row=row,
                column=0,
                sticky="ew",
                padx=16,
                pady=(16 if index == 0 else 8, 0),
            )
            row += 1
            entry = ctk.CTkEntry(self, width=300)
            if index in self._presets:
                entry.insert(0, self._presets[index])
                entry.configure(state="disabled", text_color=("#dce4ee", "#dce4ee"))
            entry.grid(row=row, column=0, sticky="ew", padx=16, pady=(2, 0))
            self._entries.append(entry)
            row += 1

        self._error_label = ctk.CTkLabel(
            self, text="", anchor="w", text_color="#e07a7a"
        )
        self._error_label.grid(row=row, column=0, sticky="ew", padx=16, pady=(8, 0))
        row += 1

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=row, column=0, sticky="e", padx=16, pady=16)
        ctk.CTkButton(
            buttons, text="Annuler", width=100, command=self._cancel
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(buttons, text="Valider", width=100, command=self._ok).pack(
            side="left"
        )

        editable = [
            entry
            for index, entry in enumerate(self._entries)
            if index not in self._presets
        ]
        if editable:
            editable[0].focus_set()

        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        try:
            self.wait_visibility()
            self.grab_set()
        except TclError:
            pass

    def _ok(self):
        if not self._entries:
            return
        values = [entry.get().strip() for entry in self._entries]
        if any(not value for value in values):
            self._error_label.configure(text="Tous les champs sont obligatoires.")
            return
        self._result = values
        self.destroy()

    def _cancel(self):
        self._result = None
        self.destroy()

    def show(self):
        self.wait_window(self)
        return self._result


class LibraryApp(ctk.CTk):
    def __init__(self, data_dir):
        super().__init__()

        self.data_dir = Path(data_dir)
        self.title("Système de Gestion de Bibliothèque Personnelle")
        self.geometry("1000x650")
        self.minsize(900, 600)

        self.journal_cpp = JournalCpp()
        self.library = core.Library()
        self.file_manager = core.FileManager(
            str(self.data_dir / "books.txt"),
            str(self.data_dir / "users.txt"),
        )

        self._poll_id = None
        self.current_tree = None
        self.buttons = {}
        self._style_tables()
        self._build_layout()
        self._load_data()

        self._poll_id = self.after(100, self._poll_journal)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        actions = {
            1: self._add_book,
            2: self._remove_book,
            3: self._search_by_title,
            4: self._search_by_author,
            7: self._add_user,
            5: self._show_all_books,
            6: self._show_available_books,
            8: self._show_all_users,
            9: self._borrow_book,
            10: self._return_book,
        }

        sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")

        ctk.CTkLabel(
            sidebar,
            text="Bibliothèque",
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(fill="x", padx=12, pady=(16, 8))

        for group, items in MENU_GROUPS:
            ctk.CTkLabel(
                sidebar,
                text=group,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
            ).pack(fill="x", padx=12, pady=(12, 4))
            for number, label in items:
                command = actions.get(number)
                button = ctk.CTkButton(
                    sidebar,
                    text=f"{number}. {label}",
                    anchor="w",
                    command=command,
                    state="normal" if command else "disabled",
                )
                button.pack(fill="x", padx=10, pady=2)
                self.buttons[number] = button

        content = ctk.CTkFrame(self, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        self.view_title = ctk.CTkLabel(
            content,
            text="Bienvenue",
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.view_title.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        self.result_frame = ctk.CTkFrame(content, corner_radius=0, fg_color="transparent")
        self.result_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        self.result_frame.grid_rowconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content,
            text="Journal",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 4))

        self.journal = ctk.CTkTextbox(content, wrap="word", state="disabled", height=110)
        self.journal.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))

        self.status = ctk.CTkLabel(self, text="Chargement…", anchor="w", height=28)
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12)

        self._show_message("Sélectionnez une action dans le menu de gauche.")

    def _style_tables(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except TclError:
            pass
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="#dce4ee",
            fieldbackground="#2b2b2b",
            bordercolor="#3a3a3a",
            borderwidth=0,
            rowheight=26,
        )
        style.configure(
            "Treeview.Heading",
            background="#333333",
            foreground="#dce4ee",
            relief="flat",
        )
        style.map("Treeview", background=[("selected", "#1f6aa5")])
        style.map("Treeview.Heading", background=[("active", "#3a3a3a")])

    def _reset_view(self, title):
        self.view_title.configure(text=title)
        self.current_tree = None
        for child in self.result_frame.winfo_children():
            child.destroy()

    def _show_message(self, text):
        for child in self.result_frame.winfo_children():
            child.destroy()
        self.current_tree = None
        ctk.CTkLabel(self.result_frame, text=text, anchor="w").grid(
            row=0, column=0, sticky="nw", padx=4, pady=4
        )

    def _make_table(self, columns, widths):
        container = ctk.CTkFrame(self.result_frame, corner_radius=0)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="browse")
        for column, width in zip(columns, widths):
            tree.heading(column, text=column)
            tree.column(column, width=width, anchor="w", stretch=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.current_tree = tree
        return tree

    def _display_books(self, title, books, empty_message):
        self._reset_view(f"{title} ({len(books)})")
        if not books:
            self._show_message(empty_message)
            return

        tree = self._make_table(
            ("Titre", "Auteur", "ISBN", "Statut", "Emprunteur"),
            (260, 180, 140, 100, 110),
        )
        for book in books:
            disponible = book.getAvailability()
            tree.insert(
                "",
                "end",
                values=(
                    book.getTitle(),
                    book.getAuthor(),
                    book.getISBN(),
                    "Disponible" if disponible else "Emprunté",
                    "—" if disponible else (book.getBorrowerId() or "—"),
                ),
            )

    def _display_users(self, title, users, empty_message):
        self._reset_view(f"{title} ({len(users)})")
        if not users:
            self._show_message(empty_message)
            return

        tree = self._make_table(
            ("Nom", "Identifiant", "Emprunts", "ISBN empruntés"),
            (200, 130, 90, 380),
        )
        for user in users:
            isbns = list(user.getBorrowedBooks())
            tree.insert(
                "",
                "end",
                values=(
                    user.getName(),
                    user.getUserId(),
                    len(isbns),
                    ", ".join(isbns) or "—",
                ),
            )

    def _prompt_fields(self, title, fields, presets=None):
        return FormDialog(self, title, fields, presets).show()

    def _add_book(self):
        values = self._prompt_fields("Ajouter un livre", ["Titre", "Auteur", "ISBN"])
        if values is None:
            return
        title, author, isbn = values
        if self.library.findBookByISBN(isbn):
            self._log(f"Erreur : Un livre avec l'ISBN {isbn} existe déjà.")
            return
        self.library.addBook(core.Book(title, author, isbn))
        self._log("Livre ajouté avec succès !")
        self._refresh_status()
        self._show_all_books()
        self._scroll_to_last_row()

    def _next_user_id(self):
        highest = 0
        for user in self.library.getAllUsers():
            match = re.fullmatch(r"USR(\d+)", user.getUserId())
            if match:
                highest = max(highest, int(match.group(1)))
        number = highest + 1
        candidate = f"USR{number:03d}"
        while self.library.findUserById(candidate):
            number += 1
            candidate = f"USR{number:03d}"
        return candidate

    def _add_user(self):
        user_id = self._next_user_id()
        values = self._prompt_fields(
            "Ajouter un utilisateur",
            ["Nom", "Identifiant"],
            presets={1: user_id},
        )
        if values is None:
            return
        name, user_id = values
        if self.library.findUserById(user_id):
            self._log(f"Erreur : Un utilisateur avec l'ID {user_id} existe déjà.")
            return
        self.library.addUser(core.User(name, user_id))
        self._log("Utilisateur ajouté avec succès !")
        self._refresh_status()
        self._show_all_users()
        self._scroll_to_last_row()

    def _remove_book(self):
        values = self._prompt_fields("Supprimer un livre", ["ISBN"])
        if values is None:
            return
        isbn = values[0]
        if self.library.removeBook(isbn):
            self._log("Livre supprimé avec succès !")
            self._refresh_status()
            self._show_all_books()
        else:
            self._log("Livre non trouvé.")

    def _borrow_book(self):
        values = self._prompt_fields(
            "Emprunter un livre", ["ISBN", "Identifiant utilisateur"]
        )
        if values is None:
            return
        isbn, user_id = values
        if self.library.checkOutBook(isbn, user_id):
            self._log("Livre emprunté avec succès !")
            self._refresh_status()
            self._show_all_books()
        else:
            self._log(
                "Erreur : Impossible d'emprunter le livre. Vérifiez l'ISBN, "
                "l'ID utilisateur et la disponibilité du livre."
            )

    def _return_book(self):
        values = self._prompt_fields("Retourner un livre", ["ISBN"])
        if values is None:
            return
        isbn = values[0]
        if self.library.returnBook(isbn):
            self._log("Livre retourné avec succès !")
            self._refresh_status()
            self._show_all_books()
        else:
            self._log(
                "Erreur : Impossible de retourner le livre. Vérifiez l'ISBN "
                "et que le livre est bien emprunté."
            )

    def _scroll_to_last_row(self):
        if self.current_tree is None:
            return
        children = self.current_tree.get_children()
        if children:
            self.current_tree.see(children[-1])

    def _prompt_search(self, title, label):
        values = FormDialog(self, title, [label]).show()
        if values is None:
            return None
        return values[0].strip() or None

    def _search_by_title(self):
        query = self._prompt_search("Recherche par titre", "Titre à rechercher")
        if query is None:
            return
        self._display_books(
            f"Recherche par titre : « {query} »",
            self.library.searchBooksByTitle(query),
            "Aucun livre trouvé avec ce titre.",
        )

    def _search_by_author(self):
        query = self._prompt_search("Recherche par auteur", "Auteur à rechercher")
        if query is None:
            return
        self._display_books(
            f"Recherche par auteur : « {query} »",
            self.library.searchBooksByAuthor(query),
            "Aucun livre trouvé de cet auteur.",
        )

    def _show_all_books(self):
        self._display_books(
            "Tous les livres",
            self.library.getAllBooks(),
            "Aucun livre dans la bibliothèque.",
        )

    def _show_available_books(self):
        self._display_books(
            "Livres disponibles",
            self.library.getAvailableBooks(),
            "Aucun livre disponible pour emprunt.",
        )

    def _show_all_users(self):
        self._display_users(
            "Tous les utilisateurs",
            self.library.getAllUsers(),
            "Aucun utilisateur enregistré.",
        )

    def _load_data(self):
        print(f"Chargement des données depuis {self.data_dir}…")
        JournalCpp.flush()
        self.file_manager.loadLibraryData(self.library)
        JournalCpp.flush()
        self._refresh_status()

    def _refresh_status(self):
        total = self.library.getTotalBooks()
        disponibles = self.library.getAvailableBookCount()
        empruntes = self.library.getCheckedOutBookCount()
        utilisateurs = len(self.library.getAllUsers())
        self.status.configure(
            text=(
                f"{total} livres · {disponibles} disponibles · "
                f"{empruntes} empruntés · {utilisateurs} utilisateurs"
            )
        )

    def _log(self, message):
        JournalCpp.flush()
        for line in self.journal_cpp.drain():
            self._append_journal(line)
        self._append_journal(message)

    def _append_journal(self, line):
        self.journal.configure(state="normal")
        self.journal.insert("end", line + "\n")
        self.journal.see("end")
        self.journal.configure(state="disabled")

    def _poll_journal(self):
        for line in self.journal_cpp.drain():
            self._append_journal(line)
        self._poll_id = self.after(100, self._poll_journal)

    def _on_close(self):
        if self._poll_id is not None:
            self.after_cancel(self._poll_id)
            self._poll_id = None
        JournalCpp.flush()
        for line in self.journal_cpp.drain():
            self._append_journal(line)
        self.journal_cpp.restore()
        self.destroy()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interface graphique du système de gestion de bibliothèque personnelle."
    )
    parser.add_argument(
        "-d",
        "--data-dir",
        default=str(BASE_DIR / "data"),
        help="répertoire des fichiers books.txt et users.txt (défaut : agent/data)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = Path(args.data_dir).expanduser()

    if not data_dir.is_dir():
        print(f"Erreur : le répertoire {data_dir} n'existe pas.", file=sys.stderr)
        return 1

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = LibraryApp(data_dir)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
