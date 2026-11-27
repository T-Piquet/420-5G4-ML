#!/usr/bin/env python3
"""Interface graphique (Tkinter) du systeme de gestion de bibliotheque.

L'interface utilise le module C++ compile avec pybind11 (bibliotheque_core).
Voir le README pour la compilation :

    mkdir build && cd build && cmake .. && make
    cd .. && python3 ui.py --data-dir data
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk

MODULE_NAME = "bibliotheque_core"

PALETTE = {
    "bg": "#111318",
    "panel": "#1a1d24",
    "panel_alt": "#222630",
    "header": "#0c0e12",
    "surface": "#2c3240",
    "border": "#363d4c",
    "text": "#e8ebf2",
    "muted": "#98a2b3",
    "accent": "#6c9cff",
    "accent_hover": "#86b0ff",
    "accent_text": "#0a1020",
    "success": "#4ade80",
    "danger": "#ff6b7a",
    "warning": "#fbbf24",
}

FONT = "DejaVu Sans"


def load_core():
    """Importe le module pybind11 en essayant les repertoires de build usuels."""
    try:
        return importlib.import_module(MODULE_NAME)
    except ImportError:
        pass

    base = Path(__file__).resolve().parent
    candidates = []
    env_path = os.environ.get("BIBLIOTHEQUE_CORE_PATH")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend([
        base / "build",
        base / "build" / "lib",
        base / "build" / "Release",
        base / "build" / "Debug",
        base,
    ])

    tried = []
    for directory in candidates:
        if not directory.is_dir():
            continue
        directory = directory.resolve()
        if directory in tried:
            continue
        tried.append(directory)
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
        try:
            return importlib.import_module(MODULE_NAME)
        except ImportError:
            continue

    raise SystemExit(
        "Module Python '{}' introuvable.\n"
        "Compilez d'abord le projet :\n"
        "  mkdir -p build && cd build && cmake .. && make\n"
        "Puis relancez : python3 ui.py --data-dir data\n"
        "Repertoires essayes : {}".format(
            MODULE_NAME,
            ", ".join(str(path) for path in tried) or "(aucun)",
        )
    )


def resolve_data_dir(value: str | None) -> Path:
    """Trouve le repertoire contenant books.txt / users.txt."""
    if value:
        path = Path(value).expanduser().resolve()
        if not path.is_dir():
            raise SystemExit("Erreur : le repertoire {} n'existe pas.".format(path))
        return path

    base = Path(__file__).resolve().parent
    candidates = [
        Path.cwd() / "data",
        Path.cwd().parent / "data",
        base / "data",
        Path.cwd(),
        base,
    ]
    for candidate in candidates:
        candidate = candidate.resolve()
        if (candidate / "books.txt").exists() or (candidate / "users.txt").exists():
            return candidate

    default = Path.cwd() / "data"
    return default if default.is_dir() else Path.cwd()


def configure_styles(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=PALETTE["bg"])
    root.option_add("*Font", (FONT, 10))
    root.option_add("*TCombobox*Listbox.background", PALETTE["panel_alt"])
    root.option_add("*TCombobox*Listbox.foreground", PALETTE["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", PALETTE["accent"])
    root.option_add("*TCombobox*Listbox.selectForeground", PALETTE["accent_text"])

    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("Panel.TFrame", background=PALETTE["panel"])
    style.configure("Header.TFrame", background=PALETTE["header"])
    style.configure("Status.TFrame", background=PALETTE["header"])
    style.configure("Stat.TFrame", background=PALETTE["panel_alt"])

    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("Panel.TLabel", background=PALETTE["panel"], foreground=PALETTE["text"])
    style.configure("Muted.TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"])
    style.configure("HeaderMuted.TLabel", background=PALETTE["header"], foreground=PALETTE["muted"])
    style.configure("Title.TLabel", background=PALETTE["header"], foreground=PALETTE["text"],
                    font=(FONT, 22, "bold"))
    style.configure("Subtitle.TLabel", background=PALETTE["header"], foreground=PALETTE["muted"],
                    font=(FONT, 10))
    style.configure("StatLabel.TLabel", background=PALETTE["panel_alt"], foreground=PALETTE["muted"],
                    font=(FONT, 9))
    style.configure("StatValue.TLabel", background=PALETTE["panel_alt"], foreground=PALETTE["accent"],
                    font=(FONT, 18, "bold"))
    style.configure("DialogTitle.TLabel", background=PALETTE["panel"], foreground=PALETTE["text"],
                    font=(FONT, 16, "bold"))
    style.configure("Field.TLabel", background=PALETTE["panel"], foreground=PALETTE["muted"],
                    font=(FONT, 10, "bold"))
    style.configure("Error.TLabel", background=PALETTE["panel"], foreground=PALETTE["danger"],
                    font=(FONT, 9))
    style.configure("Status.TLabel", background=PALETTE["header"], foreground=PALETTE["muted"],
                    font=(FONT, 9))
    style.configure("StatusSuccess.TLabel", background=PALETTE["header"], foreground=PALETTE["success"],
                    font=(FONT, 9))
    style.configure("StatusError.TLabel", background=PALETTE["header"], foreground=PALETTE["danger"],
                    font=(FONT, 9))

    style.configure("TButton", background=PALETTE["surface"], foreground=PALETTE["text"],
                    borderwidth=0, focusthickness=0, padding=(14, 9), font=(FONT, 10))
    style.map("TButton",
              background=[("pressed", PALETTE["border"]), ("active", "#353c4c")],
              foreground=[("disabled", PALETTE["muted"])])
    style.configure("Accent.TButton", background=PALETTE["accent"], foreground=PALETTE["accent_text"],
                    font=(FONT, 10, "bold"), padding=(16, 9))
    style.map("Accent.TButton",
              background=[("pressed", "#4f7fdf"), ("active", PALETTE["accent_hover"])],
              foreground=[("active", PALETTE["accent_text"])])
    style.configure("Danger.TButton", background="#3a2228", foreground=PALETTE["danger"],
                    padding=(14, 9))
    style.map("Danger.TButton", background=[("active", "#4a2a32")])
    style.configure("Ghost.TButton", background=PALETTE["panel"], foreground=PALETTE["text"],
                    padding=(14, 9))
    style.map("Ghost.TButton", background=[("active", PALETTE["surface"])])

    style.configure("Dark.TEntry", fieldbackground=PALETTE["panel_alt"],
                    foreground=PALETTE["text"], insertcolor=PALETTE["text"],
                    bordercolor=PALETTE["border"], lightcolor=PALETTE["border"],
                    darkcolor=PALETTE["border"], padding=9)
    style.map("Dark.TEntry",
              fieldbackground=[("focus", PALETTE["surface"])],
              bordercolor=[("focus", PALETTE["accent"])])

    style.configure("Dark.TCombobox", fieldbackground=PALETTE["panel_alt"],
                    background=PALETTE["surface"], foreground=PALETTE["text"],
                    arrowcolor=PALETTE["text"], bordercolor=PALETTE["border"],
                    lightcolor=PALETTE["border"], darkcolor=PALETTE["border"], padding=7)
    style.map("Dark.TCombobox",
              fieldbackground=[("readonly", PALETTE["panel_alt"])],
              foreground=[("readonly", PALETTE["text"])],
              selectbackground=[("readonly", PALETTE["panel_alt"])],
              selectforeground=[("readonly", PALETTE["text"])],
              bordercolor=[("focus", PALETTE["accent"])])

    style.configure("Treeview", background=PALETTE["panel"],
                    fieldbackground=PALETTE["panel"], foreground=PALETTE["text"],
                    rowheight=34, borderwidth=0, font=(FONT, 10))
    style.map("Treeview",
              background=[("selected", PALETTE["accent"])],
              foreground=[("selected", PALETTE["accent_text"])])
    style.configure("Treeview.Heading", background=PALETTE["panel_alt"],
                    foreground=PALETTE["muted"], relief="flat",
                    font=(FONT, 9, "bold"), padding=(8, 8))
    style.map("Treeview.Heading", background=[("active", PALETTE["surface"])])

    style.configure("Vertical.TScrollbar", background=PALETTE["surface"],
                    troughcolor=PALETTE["panel"], bordercolor=PALETTE["panel"],
                    arrowcolor=PALETTE["muted"], relief="flat")
    style.map("Vertical.TScrollbar", background=[("active", PALETTE["border"])])

    style.configure("TNotebook", background=PALETTE["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=PALETTE["panel"], foreground=PALETTE["muted"],
                    padding=(18, 9), font=(FONT, 10, "bold"), borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", PALETTE["panel_alt"])],
              foreground=[("selected", PALETTE["accent"])])

    style.configure("TSeparator", background=PALETTE["border"])
    return style


class BaseDialog(tk.Toplevel):
    """Boite de dialogue modale sombre."""

    def __init__(self, parent: tk.Misc, title: str, subtitle: str | None = None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=PALETTE["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.result = None
        self._parent = parent
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", lambda _event: self.cancel())

        outer = ttk.Frame(self, style="Panel.TFrame", padding=20)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(outer, text=title, style="DialogTitle.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(outer, text=subtitle, style="Muted.TLabel",
                      wraplength=430, justify="left").pack(anchor="w", pady=(3, 14))

        self.body = ttk.Frame(outer, style="Panel.TFrame")
        self.body.pack(fill="both", expand=True)

        self.message = tk.StringVar()
        ttk.Label(outer, textvariable=self.message, style="Error.TLabel",
                  wraplength=430, justify="left").pack(fill="x", pady=(4, 0))

        self.footer = ttk.Frame(outer, style="Panel.TFrame")
        self.footer.pack(fill="x", pady=(14, 0))

    def add_entry(self, label: str, initial: str = ""):
        ttk.Label(self.body, text=label, style="Field.TLabel").pack(anchor="w", pady=(0, 4))
        variable = tk.StringVar(value=initial)
        entry = ttk.Entry(self.body, textvariable=variable, style="Dark.TEntry", width=46)
        entry.pack(fill="x", pady=(0, 12))
        return variable, entry

    def add_combobox(self, label: str, values: list[str]):
        ttk.Label(self.body, text=label, style="Field.TLabel").pack(anchor="w", pady=(0, 4))
        variable = tk.StringVar()
        combo = ttk.Combobox(self.body, textvariable=variable, values=values,
                             state="readonly", style="Dark.TCombobox", width=40)
        combo.pack(fill="x", pady=(0, 12))
        return variable, combo

    def add_buttons(self, ok_text: str, on_ok, ok_style: str = "Accent.TButton"):
        ttk.Button(self.footer, text="Annuler", command=self.cancel,
                   style="Ghost.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(self.footer, text=ok_text, command=on_ok,
                   style=ok_style).pack(side="right")

    def set_error(self, message: str):
        self.message.set(message)

    def show(self):
        self.update_idletasks()
        width = max(self.winfo_width(), 300)
        height = max(self.winfo_height(), 150)
        parent_x = self._parent.winfo_rootx()
        parent_y = self._parent.winfo_rooty()
        parent_w = self._parent.winfo_width()
        parent_h = self._parent.winfo_height()
        x = max(parent_x + (parent_w - width) // 2, 0)
        y = max(parent_y + (parent_h - height) // 2, 0)
        self.geometry("+{}+{}".format(x, y))
        self.grab_set()
        self.focus_set()
        self.wait_window(self)

    def cancel(self):
        self.result = None
        self.destroy()


class BookDialog(BaseDialog):
    def __init__(self, parent: tk.Misc, suggested_isbn: str = ""):
        super().__init__(parent, "Ajouter un livre",
                         "Entrez le titre et l'auteur. L'ISBN est deja pre-rempli.")
        self.title_var, self.title_entry = self.add_entry("Titre")
        self.author_var, _ = self.add_entry("Auteur")
        self.isbn_var, _ = self.add_entry("ISBN (deja rempli)", initial=suggested_isbn)
        self.add_buttons("Ajouter le livre", self._on_ok)
        for widget in self.body.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.bind("<Return>", lambda _event: self._on_ok())
        self.title_entry.focus_set()
        self.show()

    def _on_ok(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        isbn = self.isbn_var.get().strip()
        if not title or not author or not isbn:
            self.set_error("Tous les champs sont obligatoires.")
            return
        self.result = (title, author, isbn)
        self.destroy()


class UserDialog(BaseDialog):
    def __init__(self, parent: tk.Misc, suggested_id: str = ""):
        super().__init__(parent, "Ajouter un utilisateur",
                         "Entrez seulement le nom. L'identifiant est deja pre-rempli.")
        self.name_var, self.name_entry = self.add_entry("Nom")
        self.id_var, _ = self.add_entry("Identifiant (deja rempli)", initial=suggested_id)
        self.add_buttons("Ajouter l'utilisateur", self._on_ok)
        for widget in self.body.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.bind("<Return>", lambda _event: self._on_ok())
        self.name_entry.focus_set()
        self.show()

    def _on_ok(self):
        name = self.name_var.get().strip()
        user_id = self.id_var.get().strip()
        if not name or not user_id:
            self.set_error("Le nom et l'identifiant sont obligatoires.")
            return
        self.result = (name, user_id)
        self.destroy()


class BorrowDialog(BaseDialog):
    def __init__(self, parent: tk.Misc, users, book_title: str):
        super().__init__(parent, "Emprunter un livre", "Livre : {}".format(book_title))
        self._ids = {}
        values = []
        for user in sorted(users, key=lambda item: item.user_id.lower()):
            label = "{} - {} ({} emprunt(s))".format(
                user.user_id, user.name, user.number_of_borrowed_books
            )
            values.append(label)
            self._ids[label] = user.user_id

        self.choice_var, self.combo = self.add_combobox("Utilisateur", values)
        if values:
            self.combo.current(0)
        self.add_buttons("Emprunter", self._on_ok)
        self.show()

    def _on_ok(self):
        choice = self.choice_var.get()
        if not choice:
            self.set_error("Choisissez un utilisateur.")
            return
        self.result = self._ids.get(choice)
        self.destroy()


class MessageDialog(BaseDialog):
    def __init__(self, parent: tk.Misc, title: str, message: str):
        super().__init__(parent, title)
        ttk.Label(self.body, text=message, style="Panel.TLabel",
                  wraplength=430, justify="left").pack(anchor="w")
        self.add_buttons("Fermer", self._close)
        self.show()

    def _close(self):
        self.result = True
        self.destroy()


class ConfirmDialog(BaseDialog):
    def __init__(self, parent: tk.Misc, title: str, message: str, danger: bool = False):
        super().__init__(parent, title)
        ttk.Label(self.body, text=message, style="Panel.TLabel",
                  wraplength=430, justify="left").pack(anchor="w")
        self.add_buttons("Confirmer", self._confirm,
                         "Danger.TButton" if danger else "Accent.TButton")
        self.show()

    def _confirm(self):
        self.result = True
        self.destroy()


def show_message(parent: tk.Misc, title: str, message: str):
    MessageDialog(parent, title, message)


def ask_confirmation(parent: tk.Misc, title: str, message: str, danger: bool = False) -> bool:
    return bool(ConfirmDialog(parent, title, message, danger=danger).result)


class LibraryApp:
    def __init__(self, root: tk.Tk, core, data_dir: Path):
        self.root = root
        self.core = core
        self.data_dir = Path(data_dir)
        self.books_file = self.data_dir / "books.txt"
        self.users_file = self.data_dir / "users.txt"

        self.library = core.Library()
        self.file_manager = core.FileManager(str(self.books_file), str(self.users_file))
        self.file_manager.load_library_data(self.library)

        self.book_query = tk.StringVar()
        self.user_query = tk.StringVar()
        self.book_filter = tk.StringVar(value="Tous les livres")
        self.status = tk.StringVar(value="Donnees : {}".format(self.data_dir))
        self._history = []

        self._book_iids: dict[str, str] = {}
        self._isbn_to_iid: dict[str, str] = {}
        self._user_iids: dict[str, str] = {}
        self._userid_to_iid: dict[str, str] = {}
        self.stat_labels: dict[str, ttk.Label] = {}

        self._build_ui()
        self._bind_events()
        self.refresh_all()
        self._update_undo_button()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        self.root.title("Bibliotheque personnelle")
        self.root.geometry("1180x740")
        self.root.minsize(1000, 640)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        header = ttk.Frame(self.root, style="Header.TFrame", padding=(24, 18))
        header.pack(side="top", fill="x")

        titles = ttk.Frame(header, style="Header.TFrame")
        titles.pack(side="left", fill="x", expand=True)
        ttk.Label(titles, text="Bibliotheque personnelle", style="Title.TLabel").pack(anchor="w")
        ttk.Label(titles, text="Livres, utilisateurs et emprunts",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        stats = ttk.Frame(header, style="Header.TFrame")
        stats.pack(side="right")
        for key, label, color in (
            ("books", "Livres", PALETTE["accent"]),
            ("available", "Disponibles", PALETTE["success"]),
            ("borrowed", "Empruntes", PALETTE["warning"]),
            ("users", "Utilisateurs", PALETTE["text"]),
        ):
            card = ttk.Frame(stats, style="Stat.TFrame", padding=(16, 9))
            card.pack(side="left", padx=(8, 0))
            ttk.Label(card, text=label, style="StatLabel.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="StatValue.TLabel")
            value.configure(foreground=color)
            value.pack(anchor="w")
            self.stat_labels[key] = value

        actions = ttk.Frame(self.root, style="Panel.TFrame", padding=(24, 10))
        actions.pack(side="top", fill="x")
        self.undo_button = ttk.Button(actions, text="Annuler", style="Ghost.TButton",
                                      command=self.undo_last)
        self.undo_button.pack(side="left")
        ttk.Button(actions, text="Enregistrer", style="Ghost.TButton",
                   command=self.save_library).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Sauvegarde", style="Ghost.TButton",
                   command=self.create_backup).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Actualiser", style="Ghost.TButton",
                   command=self.refresh_all).pack(side="left", padx=(8, 0))
        self.status_label = ttk.Label(actions, textvariable=self.status, style="Status.TLabel")
        self.status_label.pack(side="right")

        status_bar = ttk.Frame(self.root, style="Status.TFrame", padding=(24, 7))
        status_bar.pack(side="bottom", fill="x")
        ttk.Label(status_bar, text="Fichiers : {} / {}".format(
            self.books_file, self.users_file), style="Status.TLabel").pack(side="left")
        ttk.Label(status_bar, text="Ctrl+S : enregistrer", style="Status.TLabel").pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side="top", fill="both", expand=True, padx=24, pady=(8, 18))

        self._build_books_tab()
        self._build_users_tab()

    def _build_books_tab(self):
        tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=16)
        self.notebook.add(tab, text="Livres")

        toolbar = ttk.Frame(tab, style="Panel.TFrame")
        toolbar.pack(fill="x", pady=(0, 12))

        ttk.Label(toolbar, text="Recherche", style="Field.TLabel").pack(side="left", padx=(0, 8))
        search = ttk.Entry(toolbar, textvariable=self.book_query, style="Dark.TEntry", width=30)
        search.pack(side="left")
        search.insert(0, "")

        filter_box = ttk.Combobox(
            toolbar, textvariable=self.book_filter, state="readonly",
            values=["Tous les livres", "Disponibles", "Empruntes"],
            style="Dark.TCombobox", width=17,
        )
        filter_box.pack(side="left", padx=(10, 0))
        filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_books())

        self.add_book_button = ttk.Button(toolbar, text="Ajouter un livre",
                                          style="Accent.TButton",
                                          command=self.add_book)
        self.add_book_button.pack(side="right")
        self.return_button = ttk.Button(toolbar, text="Retourner",
                                        command=self.return_book)
        self.return_button.pack(side="right", padx=(0, 8))
        self.borrow_button = ttk.Button(toolbar, text="Emprunter",
                                        command=self.borrow_book)
        self.borrow_button.pack(side="right", padx=(0, 8))
        self.remove_button = ttk.Button(toolbar, text="Supprimer",
                                        style="Danger.TButton",
                                        command=self.remove_book)
        self.remove_button.pack(side="right", padx=(0, 8))

        container = ttk.Frame(tab, style="Panel.TFrame")
        container.pack(fill="both", expand=True)

        columns = ("isbn", "title", "author", "status", "borrower")
        self.books_tree = ttk.Treeview(container, columns=columns, show="headings",
                                       selectmode="browse")
        headings = {
            "isbn": ("ISBN", 150, "w"),
            "title": ("Titre", 260, "w"),
            "author": ("Auteur", 210, "w"),
            "status": ("Statut", 150, "w"),
            "borrower": ("Emprunteur", 120, "w"),
        }
        for column, (label, width, anchor) in headings.items():
            self.books_tree.heading(column, text=label)
            self.books_tree.column(column, width=width, anchor=anchor, stretch=True)
        self.books_tree.tag_configure("available", foreground=PALETTE["success"])
        self.books_tree.tag_configure("borrowed", foreground=PALETTE["warning"])

        scroll = ttk.Scrollbar(container, orient="vertical", command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scroll.set)
        self.books_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _build_users_tab(self):
        tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=16)
        self.notebook.add(tab, text="Utilisateurs")

        toolbar = ttk.Frame(tab, style="Panel.TFrame")
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Label(toolbar, text="Recherche", style="Field.TLabel").pack(side="left", padx=(0, 8))
        search = ttk.Entry(toolbar, textvariable=self.user_query, style="Dark.TEntry", width=30)
        search.pack(side="left")
        self.add_user_button = ttk.Button(toolbar, text="Ajouter un utilisateur",
                                          style="Accent.TButton",
                                          command=self.add_user)
        self.add_user_button.pack(side="right")

        container = ttk.Frame(tab, style="Panel.TFrame")
        container.pack(fill="both", expand=True)

        columns = ("id", "name", "count", "books")
        self.users_tree = ttk.Treeview(container, columns=columns, show="headings",
                                       selectmode="browse")
        headings = {
            "id": ("Identifiant", 140, "w"),
            "name": ("Nom", 240, "w"),
            "count": ("Emprunts", 100, "center"),
            "books": ("ISBN empruntes", 520, "w"),
        }
        for column, (label, width, anchor) in headings.items():
            self.users_tree.heading(column, text=label)
            self.users_tree.column(column, width=width, anchor=anchor, stretch=True)

        scroll = ttk.Scrollbar(container, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scroll.set)
        self.users_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _bind_events(self):
        self.book_query.trace_add("write", lambda *_args: self.refresh_books())
        self.user_query.trace_add("write", lambda *_args: self.refresh_users())
        self.root.bind("<Control-s>", lambda _event: self.save_library())
        self.root.bind("<F5>", lambda _event: self.refresh_all())

    # ------------------------------------------------------------- historique
    def _update_undo_button(self):
        self.undo_button.configure(
            state="normal" if self._history else "disabled"
        )

    def _snapshot(self):
        return (self.library.get_all_books(), self.library.get_all_users())

    def _remember(self, snapshot):
        self._history.append(snapshot)
        if len(self._history) > 25:
            self._history.pop(0)
        self._update_undo_button()

    def _restore(self, snapshot):
        books, users = snapshot
        library = self.core.Library()
        for book in books:
            library.add_book(book)
        for user in users:
            library.add_user(user)
        self.library = library

    def undo_last(self):
        if not self._history:
            return
        snapshot = self._history.pop()
        self._restore(snapshot)
        self.refresh_all()
        saved = self._autosave()
        self._update_undo_button()
        self.set_status(
            "Derniere action annulee."
            + ("" if saved else " Echec de l'enregistrement."),
            "success" if saved else "error",
        )

    # --------------------------------------------------------------- state
    def set_status(self, message: str, kind: str = "info"):
        self.status.set(message)
        style = {
            "success": "StatusSuccess.TLabel",
            "error": "StatusError.TLabel",
        }.get(kind, "Status.TLabel")
        self.status_label.configure(style=style)

    def _autosave(self) -> bool:
        return bool(self.file_manager.save_library_data(self.library))

    def refresh_all(self):
        self.refresh_books()
        self.refresh_users()
        self.refresh_stats()

    def refresh_stats(self):
        self.stat_labels["books"].configure(text=str(self.library.get_total_books()))
        self.stat_labels["available"].configure(
            text=str(self.library.get_available_book_count()))
        self.stat_labels["borrowed"].configure(
            text=str(self.library.get_checked_out_book_count()))
        self.stat_labels["users"].configure(text=str(len(self.library.get_all_users())))

    def refresh_books(self):
        query = self.book_query.get().strip().lower()
        mode = self.book_filter.get()

        if mode == "Disponibles":
            books = self.library.get_available_books()
        elif mode == "Empruntes":
            books = [book for book in self.library.get_all_books() if not book.available]
        else:
            books = self.library.get_all_books()

        if query:
            books = [
                book for book in books
                if query in book.title.lower()
                or query in book.author.lower()
                or query in book.isbn.lower()
            ]

        selected = self.books_tree.selection()
        selected_isbn = self._book_iids.get(selected[0]) if selected else None

        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        self._book_iids.clear()
        self._isbn_to_iid.clear()

        for index, book in enumerate(books):
            iid = "book{}".format(index)
            status = "Disponible" if book.available else "Emprunte ({})".format(book.borrower_id)
            tag = "available" if book.available else "borrowed"
            self.books_tree.insert(
                "", "end", iid=iid,
                values=(book.isbn, book.title, book.author, status,
                        book.borrower_id if book.borrower_id else "-"),
                tags=(tag,),
            )
            self._book_iids[iid] = book.isbn
            self._isbn_to_iid.setdefault(book.isbn, iid)

        if selected_isbn and selected_isbn in self._isbn_to_iid:
            iid = self._isbn_to_iid[selected_isbn]
            self.books_tree.selection_set(iid)
            self.books_tree.see(iid)

    def refresh_users(self):
        query = self.user_query.get().strip().lower()
        users = self.library.get_all_users()
        if query:
            users = [
                user for user in users
                if query in user.name.lower()
                or query in user.user_id.lower()
                or any(query in isbn.lower() for isbn in user.borrowed_books)
            ]

        selected = self.users_tree.selection()
        selected_id = self._user_iids.get(selected[0]) if selected else None

        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        self._user_iids.clear()
        self._userid_to_iid.clear()

        for index, user in enumerate(users):
            iid = "user{}".format(index)
            self.users_tree.insert(
                "", "end", iid=iid,
                values=(user.user_id, user.name, user.number_of_borrowed_books,
                        ", ".join(user.borrowed_books) or "-"),
            )
            self._user_iids[iid] = user.user_id
            self._userid_to_iid.setdefault(user.user_id, iid)

        if selected_id and selected_id in self._userid_to_iid:
            iid = self._userid_to_iid[selected_id]
            self.users_tree.selection_set(iid)
            self.users_tree.see(iid)

    def _selected_book(self):
        selection = self.books_tree.selection()
        if not selection:
            return None
        isbn = self._book_iids.get(selection[0])
        return self.library.find_book_by_isbn(isbn) if isbn else None

    # ------------------------------------------------------------- actions
    def _suggested_isbn(self) -> str:
        existing = {book.isbn for book in self.library.get_all_books()}
        numeric = [
            int(isbn) for isbn in existing
            if isbn.isdigit() and len(isbn) == 13
        ]
        candidate = max(numeric) + 1 if numeric else 9780000000001
        while str(candidate) in existing:
            candidate += 1
        return str(candidate)

    def _suggested_user_id(self) -> str:
        existing = {user.user_id for user in self.library.get_all_users()}
        number = 1
        while "USR{:03d}".format(number) in existing:
            number += 1
        return "USR{:03d}".format(number)

    def add_book(self):
        dialog = BookDialog(self.root, self._suggested_isbn())
        if not dialog.result:
            return
        title, author, isbn = dialog.result
        if self.library.find_book_by_isbn(isbn):
            show_message(self.root, "Livre deja present",
                         "Un livre avec l'ISBN {} existe deja.".format(isbn))
            return
        snapshot = self._snapshot()
        self.library.add_book(self.core.Book(title, author, isbn))
        self._remember(snapshot)
        self.refresh_all()
        saved = self._autosave()
        self.set_status(
            "Livre ajoute : {}.".format(title) + ("" if saved else " Echec de l'enregistrement."),
            "success" if saved else "error",
        )

    def add_user(self):
        dialog = UserDialog(self.root, self._suggested_user_id())
        if not dialog.result:
            return
        name, user_id = dialog.result
        if self.library.find_user_by_id(user_id):
            show_message(self.root, "Utilisateur deja present",
                         "Un utilisateur avec l'identifiant {} existe deja.".format(user_id))
            return
        snapshot = self._snapshot()
        self.library.add_user(self.core.User(name, user_id))
        self._remember(snapshot)
        self.refresh_all()
        saved = self._autosave()
        self.set_status(
            "Utilisateur ajoute : {}.".format(name)
            + ("" if saved else " Echec de l'enregistrement."),
            "success" if saved else "error",
        )

    def remove_book(self):
        book = self._selected_book()
        if not book:
            show_message(self.root, "Aucune selection",
                         "Selectionnez un livre dans la liste.")
            return
        if not book.available:
            show_message(self.root, "Livre emprunte",
                         "Impossible de supprimer un livre emprunte. Retournez-le d'abord.")
            return
        if not ask_confirmation(
            self.root, "Supprimer le livre",
            "Supprimer definitivement '{}' ({}) ?".format(book.title, book.isbn),
            danger=True,
        ):
            return
        snapshot = self._snapshot()
        if self.library.remove_book(book.isbn):
            self._remember(snapshot)
            self.refresh_all()
            saved = self._autosave()
            self.set_status(
                "Livre supprime : {}.".format(book.title)
                + ("" if saved else " Echec de l'enregistrement."),
                "success" if saved else "error",
            )
        else:
            show_message(self.root, "Erreur", "Le livre n'a pas pu etre supprime.")

    def borrow_book(self):
        book = self._selected_book()
        if not book:
            show_message(self.root, "Aucune selection",
                         "Selectionnez un livre dans la liste.")
            return
        if not book.available:
            show_message(self.root, "Livre indisponible",
                         "Ce livre est deja emprunte par {}.".format(book.borrower_id))
            return
        users = self.library.get_all_users()
        if not users:
            show_message(self.root, "Aucun utilisateur",
                         "Ajoutez d'abord un utilisateur avant d'emprunter un livre.")
            return

        dialog = BorrowDialog(self.root, users, book.title)
        if not dialog.result:
            return
        snapshot = self._snapshot()
        if self.library.check_out_book(book.isbn, dialog.result):
            self._remember(snapshot)
            self.refresh_all()
            saved = self._autosave()
            self.set_status(
                "'{}' emprunte par {}.".format(book.title, dialog.result)
                + ("" if saved else " Echec de l'enregistrement."),
                "success" if saved else "error",
            )
        else:
            show_message(self.root, "Emprunt impossible",
                         "Verifiez l'ISBN, l'utilisateur et la disponibilite du livre.")

    def return_book(self):
        book = self._selected_book()
        if not book:
            show_message(self.root, "Aucune selection",
                         "Selectionnez un livre dans la liste.")
            return
        if book.available:
            show_message(self.root, "Livre deja disponible",
                         "Ce livre n'est pas emprunte.")
            return
        snapshot = self._snapshot()
        if self.library.return_book(book.isbn):
            self._remember(snapshot)
            self.refresh_all()
            saved = self._autosave()
            self.set_status(
                "Livre retourne : {}.".format(book.title)
                + ("" if saved else " Echec de l'enregistrement."),
                "success" if saved else "error",
            )
        else:
            show_message(self.root, "Erreur", "Le livre n'a pas pu etre retourne.")

    def save_library(self):
        if self.file_manager.save_library_data(self.library):
            self.set_status("Donnees enregistrees dans {}.".format(self.data_dir), "success")
        else:
            self.set_status("Echec de l'enregistrement des donnees.", "error")
            show_message(self.root, "Erreur d'enregistrement",
                         "Impossible d'ecrire dans {}.".format(self.data_dir))

    def create_backup(self):
        if not self.file_manager.save_library_data(self.library):
            self.set_status("Echec de l'enregistrement avant la sauvegarde.", "error")
            show_message(self.root, "Erreur de sauvegarde",
                         "Impossible d'ecrire dans {}.".format(self.data_dir))
            return
        self.file_manager.create_backup()
        self.set_status("Sauvegarde creee dans {}.".format(self.data_dir), "success")

    def on_close(self):
        if not self.file_manager.save_library_data(self.library):
            self.set_status("Echec de l'enregistrement. Fermeture annulee.", "error")
            show_message(self.root, "Erreur d'enregistrement",
                         "Impossible d'enregistrer les donnees. "
                         "La fermeture a ete annulee.")
            return
        self.root.destroy()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Interface graphique de gestion de bibliotheque personnelle."
    )
    parser.add_argument("-d", "--data-dir", help="Repertoire contenant books.txt et users.txt")
    args = parser.parse_args(argv)

    core = load_core()
    data_dir = resolve_data_dir(args.data_dir)

    root = tk.Tk()
    configure_styles(root)
    LibraryApp(root, core, data_dir)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
