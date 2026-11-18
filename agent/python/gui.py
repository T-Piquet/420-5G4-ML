#!/usr/bin/env python3
"""Bibliothèque personnelle — interface graphique Tkinter.

Interface de bureau native (pas de serveur web) pour le modèle C++ exposé par
pybind11.  Elle lit et écrit les mêmes fichiers `books.txt` / `users.txt` que
l'interface texte.

    python3 agent/python/gui.py -d agent/data
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

from store import ApiError, Store

# ------------------------------------------------------------------ palette
BG = "#F5EFE3"
PAPER = "#FBF8F2"
INK = "#2A211C"
MUTED = "#6B5D52"
LINE = "#E2D8C6"
SOFT = "#EDE5D6"
FIELD = "#D9CDB8"
ACCENT = "#7A2E2A"
ACCENT_DARK = "#5A1F1C"
ACCENT_SOFT = "#F3E4E1"
OK_BG = "#DCEBE6"
OK_INK = "#1E5A55"
WARN_BG = "#F6E3CC"
WARN_LINE = "#E4C59F"
WARN_INK = "#8A4A12"
DANGER = "#9A2B26"
DANGER_BG = "#F3DAD7"
SIDEBAR_ACTIVE = "#43352D"
SPINES = ["#7A2E2A", "#1E5A55", "#A0742F", "#3B4A6B", "#5E3B52", "#4F5D3A"]

SANS = "DejaVu Sans"
SERIF = "DejaVu Serif"

F_BODY = (SANS, 10)
F_BODY_B = (SANS, 10, "bold")
F_SMALL = (SANS, 9)
F_SMALL_B = (SANS, 9, "bold")
F_TINY = (SANS, 8)
F_H1 = (SERIF, 21, "bold")
F_H2 = (SERIF, 13, "bold")
F_STAT = (SERIF, 26, "bold")
F_COVER = (SERIF, 11, "bold")


def clip(text: str, limit: int) -> str:
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def initials(name: str) -> str:
    parts = [p for p in str(name).split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n <= 1 else many}"


def normalise(value: str) -> str:
    import unicodedata

    return "".join(
        ch for ch in unicodedata.normalize("NFD", str(value))
        if unicodedata.category(ch) != "Mn"
    ).lower().strip()


# ------------------------------------------------------------------ widgets
def label(parent, text, font=F_BODY, fg=INK, bg=PAPER, anchor="w", **kwargs):
    widget = tk.Label(parent, text=text, font=font, fg=fg, bg=bg, anchor=anchor, **kwargs)
    return widget


def button(parent, text, command=None, kind="sec", small=False, state="normal", **kwargs):
    styles = {
        "pri": (ACCENT, "#FFFFFF", ACCENT_DARK),
        "sec": (PAPER, INK, "#F0E7D8"),
        "dan": (PAPER, DANGER, DANGER_BG),
        "ghost": (PAPER, MUTED, SOFT),
        "dark": (INK, BG, "#3A2E27"),
        "link": (PAPER, ACCENT, SOFT),
    }
    bg, fg, active = styles.get(kind, styles["sec"])
    if state == "disabled":
        bg, fg, active = SOFT, "#8A7C6E", SOFT
    font = (SANS, 9, "bold") if small else (SANS, 10, "bold")
    widget = tk.Button(
        parent,
        text=text,
        command=command,
        font=font,
        bg=bg,
        fg=fg,
        activebackground=active,
        activeforeground=fg,
        disabledforeground="#8A7C6E",
        relief="flat",
        bd=0,
        highlightthickness=1 if kind == "sec" else 0,
        highlightbackground=LINE,
        highlightcolor=LINE,
        padx=10 if small else 15,
        pady=4 if small else 8,
        cursor="hand2" if state != "disabled" else "arrow",
        state=state,
        **kwargs,
    )
    return widget


def card(parent, pad=18, bg=PAPER):
    outer = tk.Frame(parent, bg=bg, highlightbackground=LINE, highlightthickness=1)
    inner = tk.Frame(outer, bg=bg)
    inner.pack(fill="both", expand=True, padx=pad, pady=pad)
    return outer, inner


def separator(parent, color=SOFT, padx=0):
    line = tk.Frame(parent, bg=color, height=1, bd=0)
    line.pack(fill="x", padx=padx, pady=0)
    return line


def badge(parent, text, kind="ok"):
    bg, fg = (OK_BG, OK_INK) if kind == "ok" else (WARN_BG, WARN_INK)
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=F_SMALL_B, padx=9, pady=2)


def search_box(parent, textvariable, prefix="Rechercher", width=26):
    box = tk.Frame(parent, bg=PAPER, highlightbackground=FIELD, highlightthickness=1)
    inner = tk.Frame(box, bg=PAPER)
    inner.pack(fill="x", padx=10, pady=6)
    tk.Label(inner, text=prefix, font=F_SMALL, fg=MUTED, bg=PAPER).pack(side="left", padx=(0, 8))
    entry = tk.Entry(
        inner, textvariable=textvariable, font=F_BODY, bg=PAPER, fg=INK,
        relief="flat", bd=0, highlightthickness=0, insertbackground=INK, width=width,
    )
    entry.pack(side="left", fill="x", expand=True)
    return box, entry


class ScrollFrame(tk.Frame):
    """Vertical scrolling area; the inner frame receives the full width."""

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                bg=SOFT, troughcolor=BG, relief="flat", width=12)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._inner_changed)
        self.canvas.bind("<Configure>", self._canvas_changed)

    def _inner_changed(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _canvas_changed(self, event):
        self.canvas.itemconfigure(self._window, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def scroll(self, units):
        self.canvas.yview_scroll(units, "units")

    def to_top(self):
        self.canvas.yview_moveto(0)


# --------------------------------------------------------------------- app
class App:
    def __init__(self, root: tk.Tk, store: Store):
        self.root = root
        self.store = store
        self.state = store.state()

        self.route = "dashboard"
        self.book_isbn: str | None = None
        self.user_id: str | None = None
        self.q = ""
        self.filter = "all"
        self.bq = ""
        self.uq = ""
        self.userq = ""
        self.loan_mode = "borrow"
        self.loan_book: str | None = None
        self.loan_user: str | None = None
        self.add_error: dict | None = None
        self.add_values: dict[str, str] = {}
        self.error: str | None = None
        self.dialog: tk.Toplevel | None = None
        self._toast: tk.Label | None = None
        self.compact = False
        self._resize_job = None

        self.root.title("Bibliothèque personnelle")
        self.root.geometry("1280x860")
        self.root.minsize(1000, 640)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Control-s>", lambda _e: self.save())
        self.root.bind("<Configure>", self._on_root_configure)
        self.root.bind_all("<Button-4>", self._wheel)
        self.root.bind_all("<Button-5>", self._wheel)

        self.build_shell()
        self.show("dashboard")
        self._conflict_shown = False
        self._conflict_job = self.root.after(450, self._maybe_show_conflict)

    def _maybe_show_conflict(self):
        self._conflict_job = None
        try:
            if not self.root.winfo_exists():
                return
        except tk.TclError:
            return
        if self._conflict_shown or self.state["needsDataDir"]:
            return
        if self.state["conflicts"]:
            self._conflict_shown = True
            self.dialog_conflict(self.state["conflicts"][0])

    # ------------------------------------------------------------- shell
    def build_shell(self):
        self.side = tk.Frame(self.root, bg=INK, width=232)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)

        brand = tk.Frame(self.side, bg=INK)
        brand.pack(fill="x", padx=14, pady=(22, 18))
        logo = tk.Canvas(brand, width=32, height=32, bg=INK, highlightthickness=0)
        logo.pack(side="left", padx=(4, 10))
        for x, y, w, h, color in ((3, 7, 6, 20, "#B5473F"), (11, 4, 6, 23, "#2F8077"),
                                  (19, 9, 7, 18, "#C89545")):
            logo.create_rectangle(x, y, x + w, y + h, fill=color, outline="")
        text = tk.Frame(brand, bg=INK)
        text.pack(side="left")
        tk.Label(text, text="Bibliothèque", font=(SERIF, 15, "bold"), fg=BG, bg=INK,
                 anchor="w").pack(fill="x")
        tk.Label(text, text="personnelle", font=(SANS, 9), fg="#B9AC9A", bg=INK,
                 anchor="w").pack(fill="x")

        self.nav_buttons: dict[str, tk.Button] = {}
        nav = [
            ("dashboard", "Tableau de bord", "▦"),
            ("catalogue", "Catalogue", "▤"),
            ("users", "Utilisateurs", "☰"),
            ("loans", "Emprunter / Retourner", "⇄"),
        ]
        for key, text, glyph in nav:
            btn = self.nav_button(f"{glyph}   {text}", lambda k=key: self.show(k))
            btn.pack(fill="x", padx=10, pady=1)
            self.nav_buttons[key] = btn

        tk.Label(self.side, text="DONNÉES", font=F_TINY, fg="#B9AC9A", bg=INK,
                 anchor="w").pack(fill="x", padx=22, pady=(18, 6))
        self.data_buttons = []
        for text, command in (("Enregistrer", self.save),
                              ("Créer une sauvegarde", self.start_backup),
                              ("Quitter", self.request_quit)):
            btn = self.nav_button("◻   " + text, command)
            btn.pack(fill="x", padx=10, pady=1)
            self.data_buttons.append(btn)

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(self.main, bg=BG)
        self.header.pack(fill="x", padx=28, pady=(18, 0))
        self.title_label = tk.Label(self.header, text="", font=F_H1, fg=INK, bg=BG, anchor="w")
        self.title_label.pack(side="left", anchor="w")
        self.header_right = tk.Frame(self.header, bg=BG)
        self.header_right.pack(side="right", anchor="e")

        tk.Frame(self.main, bg=LINE, height=1).pack(fill="x", padx=28, pady=(16, 0))

        self.scroll = ScrollFrame(self.main, bg=BG)
        self.scroll.pack(fill="both", expand=True, padx=(28, 20), pady=(14, 10))
        self.content = self.scroll.inner

        self.status = tk.Frame(self.main, bg=BG)
        self.status.pack(fill="x", padx=28, pady=(0, 12))
        tk.Frame(self.status, bg=LINE, height=1).pack(fill="x", pady=(0, 8))
        self.status_left = tk.Label(self.status, text="", font=F_SMALL, fg=MUTED, bg=BG, anchor="w")
        self.status_left.pack(side="left")
        self.status_right = tk.Label(self.status, text="", font=F_SMALL_B, fg=OK_INK, bg=BG, anchor="e")
        self.status_right.pack(side="right")

    def nav_button(self, text, command):
        return tk.Button(
            self.side, text=text, font=F_BODY, fg="#E9E0D0", bg=INK,
            activebackground="#3A2E27", activeforeground="#FFFFFF",
            relief="flat", bd=0, highlightthickness=0, anchor="w",
            padx=12, pady=8, cursor="hand2", command=command,
        )

    # ------------------------------------------------------------- state
    def refresh(self):
        self.state = self.store.state()
        if self.state["needsDataDir"]:
            self.show("dashboard")
            return
        self.show(self.route)

    def book(self, isbn: str) -> dict | None:
        return next((b for b in self.state["books"] if b["isbn"] == isbn), None)

    def user(self, user_id: str) -> dict | None:
        return next((u for u in self.state["users"] if u["id"] == user_id), None)

    # ------------------------------------------------------------- shell ops
    def set_title(self, text: str):
        self.title_label.configure(text=text)

    def clear_header(self):
        for child in self.header_right.winfo_children():
            child.destroy()

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _on_root_configure(self, event):
        if event.widget is not self.root or event.width < 200:
            return
        compact = event.width < 1120
        if compact != self.compact:
            self.compact = compact
            if self._resize_job is not None:
                try:
                    self.root.after_cancel(self._resize_job)
                except Exception:
                    pass
            self._resize_job = self.root.after(120, lambda: self.show(self.route))

    def show(self, route: str, isbn: str | None = None):
        width = self.root.winfo_width()
        self.compact = width < 1120 if width > 200 else self.compact
        self.route = route
        if route == "book" and isbn is not None:
            self.book_isbn = isbn
        self.clear_header()
        self.clear_content()
        self.update_nav()
        if self.state["needsDataDir"]:
            self.screen_no_data()
            self.update_status()
            return
        screens = {
            "dashboard": self.screen_dashboard,
            "catalogue": self.screen_catalogue,
            "book": self.screen_book,
            "loans": self.screen_loans,
            "users": self.screen_users,
        }
        screens.get(route, self.screen_dashboard)()
        self.update_status()
        self.scroll.to_top()

    def update_nav(self):
        active_key = "catalogue" if self.route == "book" else self.route
        for key, btn in self.nav_buttons.items():
            active = key == active_key and not self.state["needsDataDir"]
            btn.configure(bg=SIDEBAR_ACTIVE if active else INK,
                          fg="#FFFFFF" if active else "#E9E0D0")
        normal = "normal" if not self.state["needsDataDir"] else "disabled"
        for btn in self.data_buttons:
            btn.configure(state=normal)

    def update_status(self):
        if self.state["needsDataDir"]:
            self.status_left.configure(text="Dossier de données : —")
            self.status_right.configure(text="Aucun dossier ouvert", fg=WARN_INK)
            return
        if self.compact:
            name = Path(self.state["dataDir"]).name
            self.status_left.configure(text=f"Données : {name}")
            if self.state["dirty"]:
                self.status_right.configure(
                    text=f"{self.change_title()} — Ctrl+S", fg=WARN_INK)
            else:
                self.status_right.configure(text="✓  Enregistré", fg=OK_INK)
        else:
            self.status_left.configure(
                text=f"Dossier de données : {self.state['dataDir']}   ·   "
                     + " · ".join(self.state["files"])
            )
            if self.state["dirty"]:
                self.status_right.configure(
                    text=f"{self.change_title()} — Ctrl+S pour enregistrer", fg=WARN_INK)
            else:
                self.status_right.configure(
                    text="✓  Toutes les modifications sont enregistrées", fg=OK_INK)

    def change_title(self):
        total = self.state["changes"]["total"]
        return plural(total, "modification non enregistrée", "modifications non enregistrées")

    def change_detail(self):
        changes = self.state["changes"]
        parts = []
        if changes["addedBooks"]:
            parts.append(plural(changes["addedBooks"], "livre ajouté", "livres ajoutés"))
        if changes["addedUsers"]:
            parts.append(plural(changes["addedUsers"], "utilisateur ajouté", "utilisateurs ajoutés"))
        if changes.get("editedBooks"):
            parts.append(plural(changes["editedBooks"], "livre modifié", "livres modifiés"))
        if changes["loanOps"]:
            parts.append(plural(changes["loanOps"], "emprunt", "emprunts"))
        return " · ".join(parts) or "Ctrl+S pour enregistrer"

    def banner(self, parent):
        if self.error:
            frame = tk.Frame(parent, bg=DANGER_BG, highlightbackground="#E0B7B2", highlightthickness=1)
            frame.pack(fill="x", pady=(0, 14))
            inner = tk.Frame(frame, bg=DANGER_BG)
            inner.pack(fill="x", padx=14, pady=10)
            label(inner, "Enregistrement impossible", F_BODY_B, DANGER, DANGER_BG).pack(anchor="w")
            label(inner, self.error, F_SMALL, "#7A211D", DANGER_BG, wraplength=760,
                  justify="left").pack(anchor="w")
            button(inner, "Réessayer", self.save, "pri", small=True).pack(side="right")
            return
        if self.state["dirty"]:
            frame = tk.Frame(parent, bg=WARN_BG, highlightbackground=WARN_LINE, highlightthickness=1)
            frame.pack(fill="x", pady=(0, 14))
            inner = tk.Frame(frame, bg=WARN_BG)
            inner.pack(fill="x", padx=14, pady=10)
            button(inner, "Enregistrer  Ctrl+S", self.save, "pri", small=True).pack(side="right")
            label(inner, self.change_title(), F_BODY_B, "#5E3410", WARN_BG).pack(anchor="w")
            label(inner, self.change_detail(), F_SMALL, "#5E3410", WARN_BG).pack(anchor="w")

    def toast(self, text, kind="ok"):
        if self._toast is not None and self._toast.winfo_exists():
            self._toast.destroy()
        bg = DANGER if kind == "err" else INK
        self._toast = tk.Label(self.root, text=text, font=F_BODY, bg=bg, fg=BG,
                               padx=14, pady=10, justify="left", wraplength=420)
        self._toast.place(relx=1, rely=1, x=-24, y=-52, anchor="se")
        self.root.after(4500, lambda: self._toast.destroy()
                        if self._toast is not None and self._toast.winfo_exists() else None)

    def _wheel(self, event):
        if isinstance(event.widget, (tk.Listbox, tk.Text)):
            return
        self.scroll.scroll(-1 if event.num == 4 else 1)
        return "break"

    # ------------------------------------------------------------- actions
    def save(self):
        try:
            self.state = self.store.save()
            self.error = None
            stats = self.state["stats"]
            self.toast(f"Données enregistrées — books.txt ({plural(stats['total'], 'livre', 'livres')}) · "
                       f"users.txt ({plural(stats['users'], 'utilisateur', 'utilisateurs')}).")
            self.show(self.route)
        except ApiError as exc:
            self.error = exc.message
            self.show(self.route)

    def return_book(self, isbn):
        book = self.book(isbn)
        try:
            self.state = self.store.return_loan(isbn)
            self.toast(f"« {book['title'] if book else 'Le livre'} » est de retour sur l’étagère.")
            self.show(self.route)
        except ApiError as exc:
            self.toast(exc.message, "err")

    def check_out(self):
        if not self.loan_book or not self.loan_user:
            return
        book = self.book(self.loan_book)
        user = self.user(self.loan_user)
        try:
            self.state = self.store.check_out(self.loan_book, self.loan_user)
            self.toast(f"« {book['title'] if book else 'Le livre'} » est emprunté à "
                       f"{user['name'] if user else 'l’emprunteur'}.")
            self.loan_book = None
            self.loan_user = None
            self.show("loans")
        except ApiError as exc:
            self.toast(exc.message, "err")

    def start_backup(self):
        if self.state.get("backupExists"):
            self.dialog_backup()
            return
        self.do_backup("replace")

    def do_backup(self, mode):
        try:
            self.state = self.store.backup(mode)
            files = " · ".join(self.state.get("backupFiles", []))
            self.toast(f"Sauvegarde créée : {files or 'fichiers de sauvegarde'}.")
            self.close_dialog()
            self.show(self.route)
        except ApiError as exc:
            self.toast(exc.message, "err")

    def request_quit(self):
        if self.state["dirty"]:
            self.dialog_quit()
        else:
            self.root.destroy()

    def do_quit(self, save):
        if save:
            try:
                self.store.save()
            except ApiError as exc:
                self.toast(exc.message, "err")
                return
        self.root.destroy()

    def open_dir(self, create):
        path = self.dir_var.get().strip()
        try:
            self.store.open_dir(Path(path), create=create)
            self.state = self.store.state()
            self.show("dashboard")
            self.toast(f"Dossier ouvert : {self.state['dataDir']}.")
        except ApiError as exc:
            self.toast(exc.message, "err")

    def on_close(self):
        self.request_quit()

    # ------------------------------------------------------------- dashboard
    def screen_dashboard(self):
        self.set_title("Tableau de bord")
        search_var = tk.StringVar(value=self.q)
        box, entry = search_box(self.header_right, search_var, "Rechercher",
                                width=12 if self.compact else 24)
        box.pack(side="left", padx=(0, 10))
        entry.bind("<Return>", lambda _e: self.open_catalogue(search_var.get()))
        button(self.header_right, "+ Livre" if self.compact else "+  Ajouter un livre",
               lambda: self.show("book", ""), "pri").pack(side="left")

        content = self.content
        self.banner(content)

        stats = self.state["stats"]
        row = tk.Frame(content, bg=BG)
        row.pack(fill="x")
        columns = 2 if self.compact else 4
        items = [
            ("Total des livres", str(stats["total"]), INK, None),
            ("Disponibles", str(stats["available"]), OK_INK, None),
            ("Empruntés", str(stats["checkedOut"]), WARN_INK, None),
            ("Utilisateurs", str(stats["users"]), INK,
             f"dont {stats['usersWithLoans']} avec un emprunt"),
        ]
        for index, (caption, value, color, sub) in enumerate(items):
            grid_row, grid_col = divmod(index, columns)
            outer, inner = card(row, pad=16)
            outer.grid(row=grid_row, column=grid_col, sticky="nsew",
                       padx=(0 if grid_col == 0 else 14, 0),
                       pady=(0 if grid_row == 0 else 14, 0))
            row.grid_columnconfigure(grid_col, weight=1, uniform="stat")
            label(inner, caption, F_SMALL, MUTED).pack(anchor="w")
            label(inner, value, F_STAT, color).pack(anchor="w", pady=(2, 0))
            if sub:
                label(inner, sub, F_SMALL, MUTED, wraplength=240 if self.compact else 180,
                      justify="left").pack(anchor="w")

        # shelf
        outer, inner = card(content)
        outer.pack(fill="x", pady=(22, 0))
        head = tk.Frame(inner, bg=PAPER)
        head.pack(fill="x")
        label(head, "L'étagère", F_H2).pack(side="left")
        legend = tk.Frame(head, bg=PAPER)
        legend.pack(side="right")
        for text, kind in ((f"Sur l'étagère · {stats['available']}", "full"),
                           (f"Emprunté · {stats['checkedOut']}", "gap")):
            swatch = tk.Canvas(legend, width=10, height=14, bg=PAPER, highlightthickness=0)
            if kind == "full":
                swatch.create_rectangle(0, 0, 10, 14, fill=OK_INK, outline="")
            else:
                swatch.create_rectangle(0, 0, 9, 13, outline="#A08C70", dash=(3, 2))
            swatch.pack(side="left", padx=(12, 5))
            label(legend, text, F_SMALL, MUTED).pack(side="left")

        shelf = tk.Canvas(inner, height=130, bg=PAPER, highlightthickness=0)
        shelf.pack(fill="x", pady=(12, 0))

        def draw_shelf(_event=None):
            if not shelf.winfo_exists():
                return
            shelf.delete("all")
            width = max(shelf.winfo_width(), 100)
            books = self.state["books"]
            if not books:
                return
            count = len(books)
            gap = 3
            bar = max(3.0, (width - 12 - gap * (count - 1)) / count)
            base = 112
            for index, book in enumerate(books):
                x = 6 + index * (bar + gap)
                if book["available"]:
                    height = base * (0.70 + (index * 7 % 4) * 0.09)
                    shelf.create_rectangle(x, base - height, x + bar, base,
                                           fill=SPINES[index % len(SPINES)], outline="")
                else:
                    shelf.create_rectangle(x, base - base * 0.84, x + bar, base,
                                           outline="#C9B89E", dash=(4, 3))
            shelf.create_rectangle(0, base, width, base + 8, fill="#6B4A33", outline="")

        shelf.bind("<Configure>", draw_shelf)
        label(inner, "Chaque dos = un livre, dans l'ordre du fichier books.txt. "
                     "Survolez pour voir le titre.", F_SMALL, MUTED).pack(anchor="w", pady=(8, 0))

        bottom = tk.Frame(content, bg=BG)
        bottom.pack(fill="both", expand=True, pady=(22, 0))
        bottom.grid_columnconfigure(0, weight=1, uniform="bottom")
        if not self.compact:
            bottom.grid_columnconfigure(1, weight=1, uniform="bottom")

        # loans card
        loans_outer, loans_inner = card(bottom)
        loans_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 12) if not self.compact else 0)
        head = tk.Frame(loans_inner, bg=PAPER)
        head.pack(fill="x", pady=(0, 8))
        label(head, "Emprunts en cours", F_H2).pack(side="left")
        link = tk.Button(head, text="Voir le catalogue", font=F_SMALL, fg=ACCENT, bg=PAPER,
                         relief="flat", bd=0, highlightthickness=0, cursor="hand2",
                         command=lambda: self.show("catalogue"))
        link.pack(side="right")
        self.loan_table(loans_inner, self.state["loans"], limit=7)
        if len(self.state["loans"]) > 7:
            button(loans_inner, f"Voir les {len(self.state['loans'])} emprunts",
                   lambda: self.show("loans"), "link", small=True).pack(anchor="e", pady=(8, 0))

        # right column
        right = tk.Frame(bottom, bg=BG)
        if self.compact:
            right.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        else:
            right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        if self.state["conflicts"]:
            conflict = self.state["conflicts"][0]
            alert = tk.Frame(right, bg=WARN_BG, highlightbackground=WARN_LINE, highlightthickness=1)
            alert.pack(fill="x", pady=(0, 16))
            alert_inner = tk.Frame(alert, bg=WARN_BG)
            alert_inner.pack(fill="x", padx=16, pady=14)
            label(alert_inner,
                  plural(len(self.state["conflicts"]), "incohérence dans les données",
                         "incohérences dans les données"),
                  F_BODY_B, "#5E3410", WARN_BG).pack(anchor="w")
            label(alert_inner, self.conflict_text(conflict), F_SMALL, "#5E3410", WARN_BG,
                  wraplength=420, justify="left").pack(anchor="w", pady=(4, 8))
            button(alert_inner, "Examiner", lambda c=conflict: self.dialog_conflict(c),
                   "sec", small=True).pack(anchor="w")

        authors_outer, authors_inner = card(right)
        authors_outer.pack(fill="x", pady=(0, 16))
        label(authors_inner, "Auteurs les plus présents", F_H2).pack(anchor="w", pady=(0, 12))
        maximum = self.state["authors"][0]["count"] if self.state["authors"] else 1
        for author in self.state["authors"]:
            row_frame = tk.Frame(authors_inner, bg=PAPER)
            row_frame.pack(fill="x", pady=5)
            label(row_frame, author["name"], F_BODY, INK, PAPER, width=16).pack(side="left")
            track = tk.Canvas(row_frame, height=10, bg=PAPER, highlightthickness=0)
            track.pack(side="left", fill="x", expand=True, padx=10)

            def draw_track(event, canvas=track, ratio=author["count"] / maximum):
                canvas.delete("all")
                canvas.create_rectangle(0, 0, event.width, 10, fill=SOFT, outline="")
                canvas.create_rectangle(0, 0, int(event.width * ratio), 10,
                                        fill=ACCENT, outline="")

            track.bind("<Configure>", draw_track)
            label(row_frame, str(author["count"]), F_SMALL_B, INK, PAPER, width=3,
                  anchor="e").pack(side="right")

        quick_outer, quick_inner = card(right)
        quick_outer.pack(fill="x")
        label(quick_inner, "Actions rapides", F_H2).pack(anchor="w", pady=(0, 12))
        quick = tk.Frame(quick_inner, bg=PAPER)
        quick.pack(fill="x")
        button(quick, "Emprunter un livre", lambda: self.show("loans"), "sec",
               small=self.compact).pack(side="left")
        button(quick, "Ajouter un utilisateur", lambda: self.show("users"), "sec",
               small=self.compact).pack(side="left", padx=8)
        button(quick, "Créer une sauvegarde", self.start_backup, "sec",
               small=self.compact).pack(side="left")

        self.root.after_idle(draw_shelf)

    def loan_table(self, parent, loans, limit=None):
        rows = loans if limit is None else loans[:limit]
        header = tk.Frame(parent, bg=PAPER)
        header.pack(fill="x")
        header.grid_columnconfigure(0, weight=3)
        for col, text in ((0, "LIVRE"), (1, "EMPRUNTEUR"), (2, "")):
            label(header, text, F_TINY, MUTED, PAPER).grid(row=0, column=col, sticky="w", padx=4)
        separator(parent)
        if not rows:
            label(parent, "Aucun emprunt en cours.", F_SMALL, MUTED, PAPER).pack(anchor="w", pady=10)
            return
        for loan in rows:
            row = tk.Frame(parent, bg=PAPER)
            row.pack(fill="x")
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=2)
            left = tk.Frame(row, bg=PAPER)
            left.grid(row=0, column=0, sticky="w", padx=4, pady=8)
            label(left, clip(loan["title"], 30), F_BODY_B, INK, PAPER).pack(anchor="w")
            label(left, loan["author"], F_TINY, MUTED, PAPER).pack(anchor="w")
            who = tk.Frame(row, bg=PAPER)
            who.grid(row=0, column=1, sticky="w", padx=4)
            label(who, clip(loan["userName"], 18), F_BODY, INK, PAPER).pack(anchor="w")
            label(who, loan["userId"], F_TINY, MUTED, PAPER).pack(anchor="w")
            button(row, "Retourner", lambda i=loan["isbn"]: self.return_book(i),
                   "sec", small=True).grid(row=0, column=2, sticky="e", padx=4)
            separator(parent)

    # ------------------------------------------------------------- catalogue
    def open_catalogue(self, query):
        self.q = query
        self.show("catalogue")

    def screen_catalogue(self):
        self.set_title("Catalogue")
        button(self.header_right, "+ Livre" if self.compact else "+  Ajouter un livre",
               lambda: self.show("book", ""), "pri").pack(side="right")

        content = self.content
        self.banner(content)

        filters = tk.Frame(content, bg=BG)
        filters.pack(fill="x", pady=(0, 14))
        q_var = tk.StringVar(value=self.q)
        box, entry = search_box(filters, q_var, "Rechercher", width=32)
        if self.compact:
            box.pack(fill="x")
        else:
            box.pack(side="left", fill="x", expand=True)
        q_var.trace_add("write", lambda *_: self._on_catalogue_query(q_var.get()))

        seg = tk.Frame(filters, bg=SOFT, padx=3, pady=3)
        if self.compact:
            seg.pack(anchor="w", pady=(8, 0))
        else:
            seg.pack(side="left", padx=(12, 0))
        self.filter_buttons = {}
        for key, text, count in (("all", "Tous", self.state["stats"]["total"]),
                                 ("available", "Disponibles", self.state["stats"]["available"]),
                                 ("checked", "Empruntés", self.state["stats"]["checkedOut"])):
            btn = tk.Button(seg, text=f"{text} · {count}", font=F_SMALL, bd=0, relief="flat",
                            padx=10, pady=4, cursor="hand2",
                            command=lambda k=key: self._set_filter(k))
            btn.pack(side="left", padx=1)
            self.filter_buttons[key] = btn
        self._paint_filters()

        outer, inner = card(content, pad=0)
        outer.pack(fill="x")
        self.catalogue_rows = tk.Frame(inner, bg=PAPER)
        self.catalogue_rows.pack(fill="x")
        self.catalogue_count = label(content, "", F_SMALL, MUTED, BG)
        self.catalogue_count.pack(anchor="w", pady=(8, 0))
        self.render_catalogue_rows()

    def _paint_filters(self):
        for key, btn in self.filter_buttons.items():
            active = key == self.filter
            btn.configure(bg=PAPER if active else SOFT,
                          fg=INK if active else "#4A3E35",
                          font=(SANS, 9, "bold") if active else F_SMALL,
                          activebackground=PAPER if active else "#E4DACA")

    def _set_filter(self, key):
        self.filter = key
        self._paint_filters()
        self.render_catalogue_rows()

    def _on_catalogue_query(self, value):
        self.q = value
        self.render_catalogue_rows()

    def filtered_books(self):
        query = normalise(self.q)
        books = []
        for book in self.state["books"]:
            if self.filter == "available" and not book["available"]:
                continue
            if self.filter == "checked" and book["available"]:
                continue
            if query and query not in normalise(book["title"]) and query not in normalise(book["author"]):
                continue
            books.append(book)
        return books

    def render_catalogue_rows(self):
        for child in self.catalogue_rows.winfo_children():
            child.destroy()
        compact = self.compact
        header = tk.Frame(self.catalogue_rows, bg=PAPER)
        header.pack(fill="x", padx=16, pady=(14, 0))
        columns = ((1, "TITRE", 3), (2, "STATUT", 2), (3, "ACTIONS", 1)) if compact else (
            (1, "TITRE", 3), (2, "AUTEUR", 2), (3, "ISBN", 2), (4, "STATUT", 2), (5, "ACTIONS", 1))
        for col, text, weight in columns:
            header.grid_columnconfigure(col, weight=weight)
            label(header, text, F_TINY, MUTED, PAPER).grid(row=0, column=col, sticky="w")
        separator(self.catalogue_rows)

        books = self.filtered_books()
        for index, book in enumerate(books):
            row = tk.Frame(self.catalogue_rows, bg=PAPER)
            row.pack(fill="x", padx=16)
            dot = tk.Canvas(row, width=8, height=24, bg=PAPER, highlightthickness=0)
            dot.create_rectangle(0, 0, 8, 24, fill=SPINES[index % len(SPINES)], outline="")
            dot.grid(row=0, column=0, padx=(0, 10), pady=10)

            actions = tk.Frame(row, bg=PAPER)
            if compact:
                row.grid_columnconfigure(1, weight=3)
                row.grid_columnconfigure(2, weight=1)
                cell = tk.Frame(row, bg=PAPER)
                cell.grid(row=0, column=1, sticky="w")
                tk.Button(cell, text=clip(book["title"], 30), font=F_BODY_B, fg=INK, bg=PAPER,
                          activeforeground=ACCENT, relief="flat", bd=0, highlightthickness=0,
                          anchor="w", cursor="hand2",
                          command=lambda i=book["isbn"]: self.show("book", i)).pack(anchor="w")
                label(cell, f"{clip(book['author'], 24)} · {book['isbn']}", F_TINY, MUTED,
                      PAPER).pack(anchor="w")
                status_col = 2
            else:
                row.grid_columnconfigure(1, weight=3)
                row.grid_columnconfigure(2, weight=2)
                row.grid_columnconfigure(3, weight=2)
                row.grid_columnconfigure(4, weight=2)
                row.grid_columnconfigure(5, weight=1)
                link = tk.Button(row, text=clip(book["title"], 34), font=F_BODY_B, fg=INK, bg=PAPER,
                                 activeforeground=ACCENT, relief="flat", bd=0, highlightthickness=0,
                                 anchor="w", cursor="hand2",
                                 command=lambda i=book["isbn"]: self.show("book", i))
                link.grid(row=0, column=1, sticky="w")
                label(row, clip(book["author"], 24), F_SMALL, INK, PAPER).grid(
                    row=0, column=2, sticky="w")
                label(row, book["isbn"], (SANS, 9), MUTED, PAPER).grid(
                    row=0, column=3, sticky="w")
                status_col = 4

            if book["available"]:
                status = badge(row, "✓ Disponible", "ok")
            else:
                status = badge(row, "◉ " + clip(book["borrowerName"] or book["borrowerId"], 16), "out")
            status.grid(row=0, column=status_col, sticky="w")

            action_col = status_col + 1
            row.grid_columnconfigure(action_col, weight=1)
            actions.grid(row=0, column=action_col, sticky="e")
            if book["available"]:
                button(actions, "Prêter", lambda i=book["isbn"]: self.loan_with_book(i),
                       "sec", small=True).pack(side="left")
            else:
                button(actions, "Retourner", lambda i=book["isbn"]: self.return_book(i),
                       "sec", small=True).pack(side="left")
            button(actions, "✕", lambda i=book["isbn"]: self.dialog_delete(i),
                   "dan", small=True).pack(side="left", padx=(4, 0))
            separator(self.catalogue_rows)

        if not books:
            empty = tk.Frame(self.catalogue_rows, bg=PAPER)
            empty.pack(fill="x", pady=36)
            label(empty, "Aucun livre trouvé", F_H2, INK, PAPER).pack()
            label(empty, "Aucun titre ni auteur ne correspond à cette recherche.",
                  F_SMALL, MUTED, PAPER).pack(pady=(4, 12))
            button(empty, "Ajouter ce livre", lambda: self.show("book", ""), "sec").pack()

        self.catalogue_count.configure(
            text=f"{len(books)} livre{'s' if len(books) > 1 else ''} affiché"
                 f"{'s' if len(books) > 1 else ''} sur {self.state['stats']['total']}")

    # ------------------------------------------------------------- book
    def screen_book(self):
        self.set_title("Fiche livre")
        button(self.header_right, "←  Catalogue", lambda: self.show("catalogue"),
               "sec").pack(side="right")

        content = self.content
        self.banner(content)
        book = self.book(self.book_isbn) if self.book_isbn else None

        outer, inner = card(content)
        outer.pack(fill="x")
        if book:
            top = tk.Frame(inner, bg=PAPER)
            top.pack(fill="x")
            cover = tk.Canvas(top, width=120, height=170, bg=PAPER, highlightthickness=0)
            cover.pack(side="left", padx=(0, 22))
            color = SPINES[sum(ord(c) for c in book["isbn"]) % len(SPINES)]
            cover.create_rectangle(0, 0, 120, 170, fill=color, outline="")
            cover.create_rectangle(0, 0, 6, 170, fill="#000000", outline="", stipple="gray25")
            cover.create_text(12, 14, text=book["title"], font=F_COVER, fill=BG, anchor="nw",
                              width=96)
            cover.create_text(12, 152, text=clip(book["author"], 20), font=(SANS, 8),
                              fill=BG, anchor="sw", width=96)
            meta = tk.Frame(top, bg=PAPER)
            meta.pack(side="left", fill="both", expand=True)
            label(meta, book["title"], F_H2).pack(anchor="w")
            label(meta, book["author"], F_BODY, MUTED).pack(anchor="w", pady=(2, 10))
            if book["available"]:
                badge(meta, "✓ Disponible", "ok").pack(anchor="w")
            else:
                badge(meta, "◉ Emprunté par " + (book["borrowerName"] or "utilisateur inconnu"),
                      "out").pack(anchor="w")

            fields = tk.Frame(inner, bg=PAPER)
            fields.pack(fill="x", pady=(18, 0))
            rows = [("Titre", book["title"]), ("Auteur", book["author"]),
                    ("ISBN", book["isbnFormatted"]),
                    ("Statut", "Disponible" if book["available"] else "Emprunté")]
            for index, (key, value) in enumerate(rows):
                label(fields, key, F_SMALL, MUTED, PAPER, width=14).grid(
                    row=index, column=0, sticky="w", pady=4)
                label(fields, value,
                      font=(SANS, 9) if key == "ISBN" else F_BODY,
                      fg=INK, bg=PAPER).grid(
                    row=index, column=1, sticky="w", pady=4)
            label(fields, "Emprunteur", F_SMALL, MUTED, PAPER, width=14).grid(
                row=4, column=0, sticky="w", pady=4)
            if book["borrowerId"]:
                borrower = tk.Button(
                    fields, text=book["borrowerName"] or book["borrowerId"],
                    font=F_BODY, fg=ACCENT, bg=PAPER, relief="flat", bd=0,
                    highlightthickness=0, cursor="hand2",
                    command=lambda uid=book["borrowerId"]: self.open_user(uid))
                borrower.grid(row=4, column=1, sticky="w")
                label(fields, "· " + book["borrowerId"], F_SMALL, MUTED, PAPER).grid(
                    row=4, column=2, sticky="w")
            else:
                label(fields, "—", F_BODY, MUTED, PAPER).grid(row=4, column=1, sticky="w")

            actions = tk.Frame(inner, bg=PAPER)
            actions.pack(fill="x", pady=(16, 0))
            if not book["available"]:
                button(actions, "Retourner le livre",
                       lambda i=book["isbn"]: self.return_book(i), "pri").pack(side="left")
            button(actions, "Modifier", lambda i=book["isbn"]: self.dialog_edit(i),
                   "sec").pack(side="left", padx=8)
            if book["available"]:
                button(actions, "Supprimer", lambda i=book["isbn"]: self.dialog_delete(i),
                       "dan").pack(side="left")
            else:
                button(actions, "Supprimer", None, "sec", state="disabled").pack(side="left")
                note = tk.Frame(inner, bg="#F0E7D8")
                note.pack(fill="x", pady=(16, 0))
                label(note, "Un livre emprunté ne peut pas être supprimé : retournez-le d'abord, "
                            f"pour que la liste de {book['borrowerName'] or 'l’emprunteur'} reste à jour.",
                      F_SMALL, "#4A3E35", "#F0E7D8", wraplength=520, justify="left").pack(
                    anchor="w", padx=12, pady=10)
        else:
            empty = tk.Frame(inner, bg=PAPER)
            empty.pack(fill="x", pady=30)
            label(empty, "Aucun livre sélectionné", F_H2, INK, PAPER).pack()
            label(empty, "Choisissez un livre dans le catalogue pour voir sa fiche.",
                  F_SMALL, MUTED, PAPER).pack(pady=(4, 12))
            button(empty, "Ouvrir le catalogue", lambda: self.show("catalogue"),
                   "sec").pack()

        self.add_book_card()

    def add_book_card(self):
        outer, inner = card(self.content)
        outer.pack(fill="x", pady=(22, 0))
        label(inner, "Ajouter un livre", F_H2).pack(anchor="w")
        label(inner, "Tous les champs sont obligatoires. Le caractère « | » n'est pas accepté.",
              F_SMALL, MUTED).pack(anchor="w", pady=(2, 14))

        values = self.add_values
        error = self.add_error or {}
        self.entry_title = self.form_field(inner, "Titre", values.get("title", ""), error, "title")
        self.entry_author = self.form_field(inner, "Auteur", values.get("author", ""), error, "author")
        self.entry_isbn = self.form_field(inner, "ISBN", values.get("isbn", ""), error, "isbn")

        if error.get("code") == "duplicate_isbn":
            dup = tk.Frame(inner, bg=PAPER)
            dup.pack(fill="x", pady=(2, 0))
            label(dup, f"Un livre avec l'ISBN {error.get('existingIsbn', '')} existe déjà : ",
                  F_SMALL, DANGER).pack(side="left")
            tk.Button(dup, text=error.get("existingTitle", "voir le livre"), font=F_SMALL_B,
                      fg=DANGER, bg=PAPER, relief="flat", bd=0, cursor="hand2",
                      command=lambda: self.show("book", error.get("existingIsbn", ""))).pack(side="left")
        label(inner, "Tirets et espaces ignorés — 13 chiffres attendus.",
              F_SMALL, MUTED).pack(anchor="w", pady=(2, 12))

        actions = tk.Frame(inner, bg=PAPER)
        actions.pack(fill="x")
        button(actions, "Ajouter le livre", self.submit_book, "pri").pack(side="right")
        button(actions, "Annuler", lambda: self.show("catalogue"), "sec").pack(
            side="right", padx=(0, 8))

    def form_field(self, parent, caption, value, error, field):
        frame = tk.Frame(parent, bg=PAPER)
        frame.pack(fill="x", pady=(0, 10))
        label(frame, caption, F_SMALL_B, INK).pack(anchor="w")
        entry = tk.Entry(frame, font=F_BODY, bg="#FFFFFF", fg=INK, relief="flat", bd=0,
                         highlightthickness=1,
                         highlightbackground=DANGER if error.get("field") == field else FIELD,
                         highlightcolor=ACCENT, insertbackground=INK)
        entry.pack(fill="x", ipady=8, pady=(4, 0))
        entry.insert(0, value)
        if error.get("field") == field:
            label(frame, error.get("message", ""), F_SMALL, DANGER).pack(anchor="w", pady=(3, 0))
        return entry

    def submit_book(self):
        title = self.entry_title.get()
        author = self.entry_author.get()
        isbn = self.entry_isbn.get()
        self.add_values = {"title": title, "author": author, "isbn": isbn}
        try:
            self.state = self.store.add_book(title, author, isbn)
            self.add_error = None
            self.add_values = {}
            added = self.state["books"][-1]
            self.toast("Livre ajouté.")
            self.show("book", added["isbn"])
        except ApiError as exc:
            self.add_error = {"field": exc.field, "message": exc.message, "code": exc.code,
                              "existingIsbn": exc.extra.get("existingIsbn"),
                              "existingTitle": exc.extra.get("existingTitle")}
            self.show("book", self.book_isbn or "")

    # ------------------------------------------------------------- loans
    def loan_with_book(self, isbn):
        self.loan_book = isbn
        self.loan_mode = "borrow"
        self.show("loans")

    def open_user(self, user_id):
        self.user_id = user_id
        self.show("users")

    def screen_loans(self):
        self.set_title("Emprunter / Retourner")
        mode_frame = tk.Frame(self.header_right, bg=SOFT, padx=3, pady=3)
        mode_frame.pack(side="right")
        for key, text in (("borrow", "Emprunter"),
                          ("return", f"Retourner · {self.state['stats']['checkedOut']}")):
            active = self.loan_mode == key
            tk.Button(mode_frame, text=text, font=(SANS, 9, "bold") if active else F_SMALL,
                      bg=PAPER if active else SOFT, fg=INK if active else "#4A3E35",
                      activebackground=PAPER if active else "#E4DACA", relief="flat", bd=0,
                      padx=12, pady=5, cursor="hand2",
                      command=lambda k=key: self._set_loan_mode(k)).pack(side="left", padx=1)

        content = self.content
        self.banner(content)
        if self.loan_mode == "return":
            outer, inner = card(content, pad=0)
            outer.pack(fill="x")
            body = tk.Frame(inner, bg=PAPER)
            body.pack(fill="x", padx=18, pady=16)
            label(body, "Livres actuellement empruntés", F_H2).pack(anchor="w", pady=(0, 10))
            self.loan_table(body, self.state["loans"])
            return

        cols = tk.Frame(content, bg=BG)
        cols.pack(fill="x")
        cols.grid_columnconfigure(0, weight=1, uniform="loan")
        if not self.compact:
            cols.grid_columnconfigure(1, weight=1, uniform="loan")

        # step 1
        left_outer, left_inner = card(cols)
        left_outer.grid(row=0, column=0, sticky="nsew",
                        padx=(0, 12) if not self.compact else 0)
        step_title(left_inner, "1", "Choisir un livre disponible")
        self.bq_var = tk.StringVar(value=self.bq)
        box, entry = search_box(left_inner, self.bq_var, "Filtrer", width=26)
        box.pack(fill="x", pady=(10, 8))
        self.bq_var.trace_add("write", lambda *_: self._fill_loan_books())
        self.book_list = tk.Listbox(left_inner, height=8 if self.compact else 9, font=F_BODY, bg=PAPER, fg=INK,
                                    selectbackground=ACCENT_SOFT, selectforeground=INK,
                                    relief="flat", bd=0, highlightthickness=1,
                                    highlightbackground=LINE, activestyle="none",
                                    exportselection=False)
        self.book_list.pack(fill="x")
        self.book_list.bind("<<ListboxSelect>>", self._pick_loan_book)
        label(left_inner, "Seuls les livres disponibles sont proposés — plus besoin de saisir l'ISBN.",
              F_SMALL, MUTED, wraplength=380, justify="left").pack(anchor="w", pady=(8, 0))
        self._fill_loan_books()

        # step 2
        right_outer, right_inner = card(cols)
        if self.compact:
            right_outer.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        else:
            right_outer.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        step_title(right_inner, "2", "Choisir l'emprunteur")
        self.uq_var = tk.StringVar(value=self.uq)
        box, entry = search_box(right_inner, self.uq_var, "Filtrer", width=24)
        box.pack(fill="x", pady=(10, 8))
        self.uq_var.trace_add("write", lambda *_: self._fill_loan_users())
        self.user_list = tk.Listbox(right_inner, height=8 if self.compact else 9, font=F_BODY, bg=PAPER, fg=INK,
                                    selectbackground=ACCENT_SOFT, selectforeground=INK,
                                    relief="flat", bd=0, highlightthickness=1,
                                    highlightbackground=LINE, activestyle="none",
                                    exportselection=False)
        self.user_list.pack(fill="x")
        self.user_list.bind("<<ListboxSelect>>", self._pick_loan_user)
        tk.Button(right_inner, text="+  Nouvel utilisateur", font=F_SMALL_B, fg=ACCENT,
                  bg=PAPER, relief="flat", bd=0, highlightthickness=0, cursor="hand2",
                  command=lambda: self.show("users")).pack(anchor="w", pady=(8, 0))
        self._fill_loan_users()

        # summary
        summary = tk.Frame(content, bg=INK)
        summary.pack(fill="x", pady=(18, 0))
        summary_inner = tk.Frame(summary, bg=INK)
        summary_inner.pack(fill="x", padx=18, pady=14)
        text = tk.Frame(summary_inner, bg=INK)
        text.pack(side="left", fill="x", expand=True)
        self.summary_book = tk.Label(text, text="Aucun livre choisi", font=F_BODY_B, fg=BG, bg=INK,
                                     anchor="w")
        self.summary_book.pack(anchor="w")
        self.summary_detail = tk.Label(text, text="Choisissez un livre disponible à l’étape 1",
                                       font=F_SMALL, fg="#C9BCA9", bg=INK, anchor="w")
        self.summary_detail.pack(anchor="w")
        self.summary_user = tk.Label(text, text="Choisissez un emprunteur à l’étape 2",
                                     font=F_SMALL, fg="#C9BCA9", bg=INK, anchor="w")
        self.summary_user.pack(anchor="w", pady=(4, 0))
        self.confirm_button = button(summary_inner, "Confirmer l’emprunt", self.check_out,
                                     "pri", state="disabled")
        self.confirm_button.pack(side="right")
        button(summary_inner, "Annuler", self._reset_loan, "dark").pack(side="right", padx=(8, 0))
        self._paint_summary()

    def _set_loan_mode(self, mode):
        self.loan_mode = mode
        self.show("loans")

    def _fill_loan_books(self):
        self.book_list.delete(0, "end")
        self.book_choices = []
        query = normalise(self.bq_var.get() if hasattr(self, "bq_var") else "")
        for book in self.state["books"]:
            if not book["available"]:
                continue
            if query and query not in normalise(book["title"]) and query not in normalise(book["author"]):
                continue
            self.book_choices.append(book["isbn"])
            self.book_list.insert("end", f"{clip(book['title'], 34)} — {clip(book['author'], 22)}")
        if self.loan_book in self.book_choices:
            index = self.book_choices.index(self.loan_book)
            self.book_list.selection_set(index)
            self.book_list.see(index)

    def _fill_loan_users(self):
        self.user_list.delete(0, "end")
        self.user_choices = []
        query = normalise(self.uq_var.get() if hasattr(self, "uq_var") else "")
        for user in self.state["users"]:
            if query and query not in normalise(user["name"]) and query not in normalise(user["id"]):
                continue
            self.user_choices.append(user["id"])
            count = "aucun prêt" if user["borrowCount"] == 0 else plural(user["borrowCount"], "prêt", "prêts")
            self.user_list.insert("end", f"{clip(user['name'], 24)} · {user['id']} · {count}")
        if self.loan_user in self.user_choices:
            index = self.user_choices.index(self.loan_user)
            self.user_list.selection_set(index)
            self.user_list.see(index)

    def _pick_loan_book(self, _event=None):
        selection = self.book_list.curselection()
        if selection:
            self.loan_book = self.book_choices[selection[0]]
            self._paint_summary()

    def _pick_loan_user(self, _event=None):
        selection = self.user_list.curselection()
        if selection:
            self.loan_user = self.user_choices[selection[0]]
            self._paint_summary()

    def _reset_loan(self):
        self.loan_book = None
        self.loan_user = None
        self._paint_summary()
        if hasattr(self, "book_list"):
            self.book_list.selection_clear(0, "end")
            self.user_list.selection_clear(0, "end")

    def _paint_summary(self):
        book = self.book(self.loan_book) if self.loan_book else None
        user = self.user(self.loan_user) if self.loan_user else None
        self.summary_book.configure(text=book["title"] if book else "Aucun livre choisi")
        self.summary_detail.configure(
            text=f"{book['author']} · {book['isbn']}" if book
            else "Choisissez un livre disponible à l’étape 1")
        self.summary_user.configure(
            text=f"Pour {user['name']} ({user['id']})" if user
            else "Choisissez un emprunteur à l’étape 2")
        self.confirm_button.configure(
            state="normal" if book and user else "disabled",
            bg=ACCENT if book and user else SOFT,
            fg="#FFFFFF" if book and user else "#8A7C6E",
            cursor="hand2" if book and user else "arrow")

    # ------------------------------------------------------------- users
    def screen_users(self):
        self.set_title("Utilisateurs")
        note = (f"{self.state['stats']['users']} inscrits · "
                f"{self.state['stats']['usersWithLoans']} prêts" if self.compact else
                f"{self.state['stats']['users']} inscrits · "
                f"{self.state['stats']['usersWithLoans']} avec un emprunt")
        label(self.header_right, note, F_BODY, MUTED, BG).pack(side="right")

        content = self.content
        self.banner(content)
        layout = tk.Frame(content, bg=BG)
        layout.pack(fill="both", expand=True)
        if self.compact:
            layout.grid_columnconfigure(0, weight=1)
        else:
            layout.grid_columnconfigure(0, weight=0, minsize=330)
            layout.grid_columnconfigure(1, weight=1)

        left_outer, left_inner = card(layout)
        left_outer.grid(row=0, column=0, sticky="nsew",
                        padx=(0, 16) if not self.compact else 0)
        self.userq_var = tk.StringVar(value=self.userq)
        box, _entry = search_box(left_inner, self.userq_var, "Nom ou ID", width=22)
        box.pack(fill="x")
        self.userq_var.trace_add("write", lambda *_: self._fill_users())
        self.users_listbox = tk.Listbox(left_inner, height=8 if self.compact else 15, font=F_BODY, bg=PAPER, fg=INK,
                                        selectbackground=ACCENT_SOFT, selectforeground=INK,
                                        relief="flat", bd=0, highlightthickness=1,
                                        highlightbackground=LINE, activestyle="none",
                                        exportselection=False)
        self.users_listbox.pack(fill="both", expand=True, pady=(10, 0))
        self.users_listbox.bind("<<ListboxSelect>>", self._pick_user)
        self._fill_users()

        right = tk.Frame(layout, bg=BG)
        if self.compact:
            right.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        else:
            right.grid(row=0, column=1, sticky="nsew")
        self.user_detail = tk.Frame(right, bg=BG)
        self.user_detail.pack(fill="x")
        self.render_user_detail()
        self.add_user_card(right)

    def _fill_users(self):
        self.users_listbox.delete(0, "end")
        self.user_choices = []
        query = normalise(self.userq_var.get() if hasattr(self, "userq_var") else "")
        for user in self.state["users"]:
            if query and query not in normalise(user["name"]) and query not in normalise(user["id"]):
                continue
            self.user_choices.append(user["id"])
            count = "aucun prêt" if user["borrowCount"] == 0 else plural(user["borrowCount"], "prêt", "prêts")
            self.users_listbox.insert("end", f"{clip(user['name'], 24)} · {user['id']} · {count}")
        if self.user_id not in self.user_choices and self.user_choices:
            self.user_id = self.user_choices[0]
        if self.user_id in self.user_choices:
            index = self.user_choices.index(self.user_id)
            self.users_listbox.selection_set(index)
            self.users_listbox.see(index)

    def _pick_user(self, _event=None):
        selection = self.users_listbox.curselection()
        if selection:
            self.user_id = self.user_choices[selection[0]]
            self.render_user_detail()

    def render_user_detail(self):
        for child in self.user_detail.winfo_children():
            child.destroy()
        user = self.user(self.user_id) if self.user_id else None
        outer, inner = card(self.user_detail, pad=22)
        outer.pack(fill="x")
        if not user:
            label(inner, "Aucun utilisateur", F_H2).pack(anchor="w")
            label(inner, "Ajoutez un premier utilisateur pour commencer.", F_SMALL, MUTED).pack(
                anchor="w", pady=(4, 0))
            return

        head = tk.Frame(inner, bg=PAPER)
        head.pack(fill="x")
        avatar = tk.Canvas(head, width=64, height=64, bg=PAPER, highlightthickness=0)
        avatar.create_oval(0, 0, 64, 64, fill=INK, outline="")
        avatar.create_text(32, 32, text=initials(user["name"]), font=(SERIF, 18, "bold"), fill=BG)
        avatar.pack(side="left", padx=(0, 16))
        meta = tk.Frame(head, bg=PAPER)
        meta.pack(side="left", fill="x", expand=True)
        label(meta, user["name"], (SERIF, 18, "bold")).pack(anchor="w")
        label(meta, f"ID {user['id']} · "
                    + ("aucun prêt" if user["borrowCount"] == 0
                       else plural(user["borrowCount"], "prêt en cours", "prêts en cours")),
              F_SMALL, MUTED).pack(anchor="w")
        button(head, "Prêter un livre", lambda uid=user["id"]: self.loan_for_user(uid),
               "pri").pack(side="right")

        label(inner, "LIVRES EMPRUNTÉS", F_TINY, MUTED).pack(anchor="w", pady=(20, 8))
        if not user["books"]:
            empty = tk.Frame(inner, bg=PAPER, highlightbackground=FIELD, highlightthickness=1)
            empty.pack(fill="x")
            label(empty, "Aucun livre emprunté pour le moment.", F_SMALL, MUTED).pack(pady=18)
        for book in user["books"]:
            row = tk.Frame(inner, bg="#FFFFFF", highlightbackground=LINE, highlightthickness=1)
            row.pack(fill="x", pady=3)
            row_inner = tk.Frame(row, bg="#FFFFFF")
            row_inner.pack(fill="x", padx=12, pady=8)
            spine = tk.Canvas(row_inner, width=8, height=32, bg="#FFFFFF", highlightthickness=0)
            spine.create_rectangle(0, 0, 8, 32, fill=SPINES[
                sum(ord(c) for c in book["isbn"]) % len(SPINES)], outline="")
            spine.pack(side="left", padx=(0, 10))
            text = tk.Frame(row_inner, bg="#FFFFFF")
            text.pack(side="left", fill="x", expand=True)
            label(text, book["title"], F_BODY_B, INK, "#FFFFFF").pack(anchor="w")
            label(text, f"{book['author']} · ISBN {book['isbn']}", F_SMALL, MUTED,
                  "#FFFFFF").pack(anchor="w")
            button(row_inner, "Retourner", lambda i=book["isbn"]: self.return_book(i),
                   "sec", small=True).pack(side="right")

        conflict = next((c for c in self.state["conflicts"] if c["userId"] == user["id"]), None)
        if conflict:
            warn = tk.Frame(inner, bg=WARN_BG, highlightbackground=WARN_LINE, highlightthickness=1)
            warn.pack(fill="x", pady=(12, 0))
            label(warn, "Incohérence : " + self.conflict_text(conflict), F_SMALL, "#5E3410",
                  WARN_BG, wraplength=520, justify="left").pack(anchor="w", padx=12, pady=(8, 2))
            button(warn, "Corriger", lambda c=conflict: self.dialog_conflict(c),
                   "sec", small=True).pack(anchor="w", padx=12, pady=(0, 8))

    def add_user_card(self, parent):
        outer, inner = card(parent, pad=22)
        outer.pack(fill="x", pady=(18, 0))
        label(inner, "Ajouter un utilisateur", F_H2).pack(anchor="w")
        form = tk.Frame(inner, bg=PAPER)
        form.pack(fill="x", pady=(12, 0))
        name_frame = tk.Frame(form, bg=PAPER)
        name_frame.pack(side="left", fill="x", expand=True)
        label(name_frame, "Nom", F_SMALL_B).pack(anchor="w")
        self.new_name = tk.Entry(name_frame, font=F_BODY, bg="#FFFFFF", fg=INK, relief="flat",
                                 bd=0, highlightthickness=1, highlightbackground=FIELD,
                                 highlightcolor=ACCENT)
        self.new_name.pack(fill="x", ipady=8, pady=(4, 0))
        id_frame = tk.Frame(form, bg=PAPER)
        id_frame.pack(side="left", padx=12)
        label(id_frame, "ID", F_SMALL_B).pack(anchor="w")
        next_id = f"USR{max([int(u['id'][3:]) for u in self.state['users'] if u['id'][3:].isdigit()] or [0]) + 1:03d}"
        entry = tk.Entry(id_frame, font=F_BODY, bg=SOFT, fg=MUTED, relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=FIELD, width=10)
        entry.insert(0, next_id)
        entry.configure(state="readonly", readonlybackground=SOFT)
        entry.pack(ipady=8, pady=(4, 0))
        button(form, "Ajouter", self.submit_user, "pri").pack(side="left", pady=(18, 0))
        label(inner, "L'ID est attribué automatiquement — plus de doublons possibles.",
              F_SMALL, MUTED).pack(anchor="w", pady=(8, 0))

    def submit_user(self):
        name = self.new_name.get().strip()
        if not name:
            self.toast("Le nom est obligatoire.", "err")
            return
        try:
            self.state = self.store.add_user(name)
            created = self.state["users"][-1]
            self.user_id = created["id"]
            self.toast(f"Utilisateur ajouté : {created['name']}.")
            self.show("users")
        except ApiError as exc:
            self.toast(exc.message, "err")

    def loan_for_user(self, user_id):
        self.loan_user = user_id
        self.loan_mode = "borrow"
        self.show("loans")

    # ------------------------------------------------------------- no data
    def screen_no_data(self):
        self.set_title("Bibliothèque personnelle")
        outer, inner = card(self.content, pad=24)
        outer.pack(fill="x", pady=20)
        label(inner, "Aucun dossier de données", F_H2).pack(anchor="w")
        label(inner, "Lancé sans -d : choisissez un dossier contenant books.txt et users.txt.",
              F_SMALL, MUTED).pack(anchor="w", pady=(4, 16))
        self.dir_var = tk.StringVar(value="agent/data")
        label(inner, "Dossier de données", F_SMALL_B).pack(anchor="w")
        entry = tk.Entry(inner, textvariable=self.dir_var, font=F_BODY, bg="#FFFFFF", fg=INK,
                         relief="flat", bd=0, highlightthickness=1, highlightbackground=FIELD,
                         highlightcolor=ACCENT)
        entry.pack(fill="x", ipady=8, pady=(4, 14))
        actions = tk.Frame(inner, bg=PAPER)
        actions.pack(fill="x")
        button(actions, "Nouvelle bibliothèque", lambda: self.open_dir(True), "pri").pack(side="left")
        button(actions, "Ouvrir un dossier…", lambda: self.open_dir(False), "sec").pack(
            side="left", padx=8)

    # ------------------------------------------------------------- dialogs
    def _dialog(self, title_text, width=560):
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.destroy()
        top = tk.Toplevel(self.root)
        top.title("Bibliothèque personnelle")
        top.configure(bg=PAPER)
        top.transient(self.root)
        top.resizable(False, False)
        top.grab_set()
        body = tk.Frame(top, bg=PAPER)
        body.pack(fill="both", expand=True, padx=24, pady=22)
        label(body, title_text, (SERIF, 15, "bold")).pack(anchor="w")
        content = tk.Frame(body, bg=PAPER)
        content.pack(fill="x", pady=(10, 0))
        actions = tk.Frame(body, bg=PAPER)
        actions.pack(fill="x", pady=(18, 0))
        top.update_idletasks()
        height = max(180, top.winfo_reqheight())
        x = self.root.winfo_rootx() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - height) // 2
        top.geometry(f"{width}x{height}+{max(x, 20)}+{max(y, 20)}")
        self.dialog = top
        return top, content, actions

    def close_dialog(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.destroy()
        self.dialog = None

    def dialog_backup(self):
        top, content, actions = self._dialog("Une sauvegarde existe déjà")
        label(content, "books.txt.backup et users.txt.backup sont déjà présents dans "
                       f"{self.state['dataDir']}.", F_SMALL, "#4A3E35", PAPER,
              wraplength=500, justify="left").pack(anchor="w", pady=(0, 10))
        mode = tk.StringVar(value="dated")
        for value, text in (("dated", "Créer une sauvegarde datée"),
                            ("replace", "Remplacer l'ancienne sauvegarde")):
            tk.Radiobutton(content, text=text, variable=mode, value=value, font=F_BODY,
                           bg=PAPER, fg=INK, activebackground=PAPER, selectcolor=PAPER,
                           anchor="w", cursor="hand2").pack(fill="x", pady=2)
        button(actions, "Créer la sauvegarde", lambda: self.do_backup(mode.get()),
               "pri").pack(side="right")
        button(actions, "Annuler", self.close_dialog, "sec").pack(side="right", padx=(0, 8))

    def dialog_quit(self):
        top, content, actions = self._dialog("Enregistrer avant de quitter ?")
        label(content, f"Vous avez {self.change_title().lower()}. Sans enregistrement, "
                       f"{'elles seront perdues' if self.state['changes']['total'] > 1 else 'elle sera perdue'}.",
              F_SMALL, "#4A3E35", PAPER, wraplength=480, justify="left").pack(anchor="w")
        button(actions, "Enregistrer et quitter", lambda: self.do_quit(True), "pri").pack(side="right")
        button(actions, "Annuler", self.close_dialog, "sec").pack(side="right", padx=(0, 8))
        button(actions, "Quitter sans enregistrer", lambda: self.do_quit(False),
               "dan").pack(side="right", padx=(0, 8))

    def dialog_delete(self, isbn):
        book = self.book(isbn)
        if not book:
            return
        top, content, actions = self._dialog(f"Supprimer « {book['title']} » ?", width=580)
        if book["available"]:
            label(content, "Le livre sera retiré du catalogue. Cette action ne peut pas être annulée.",
                  F_SMALL, "#4A3E35", PAPER, wraplength=500, justify="left").pack(anchor="w")
            button(actions, "Supprimer", lambda: self.delete_book(isbn, False),
                   "pri").pack(side="right")
        else:
            label(content, f"Ce livre est actuellement emprunté par "
                           f"{book['borrowerName'] or book['borrowerId']} ({book['borrowerId']}). "
                           "Le supprimer le retirera aussi de sa liste d'emprunts.",
                  F_SMALL, "#4A3E35", PAPER, wraplength=500, justify="left").pack(anchor="w")
            button(actions, "Retourner et supprimer", lambda: self.delete_book(isbn, True),
                   "pri").pack(side="right")
            button(actions, "Retourner d'abord",
                   lambda: (self.close_dialog(), self.return_book(isbn)),
                   "sec").pack(side="right", padx=(0, 8))
        button(actions, "Annuler", self.close_dialog, "sec").pack(side="right", padx=(0, 8))

    def delete_book(self, isbn, return_first):
        book = self.book(isbn)
        try:
            self.state = self.store.remove_book(isbn, return_first=return_first)
            self.close_dialog()
            self.toast(f"« {book['title'] if book else 'Le livre'} » a été supprimé.")
            if self.route == "book":
                self.show("catalogue")
            else:
                self.show(self.route)
        except ApiError as exc:
            self.close_dialog()
            self.toast(exc.message, "err")

    def dialog_edit(self, isbn):
        book = self.book(isbn)
        if not book:
            return
        top, content, actions = self._dialog("Modifier le livre")
        label(content, "Titre", F_SMALL_B).pack(anchor="w")
        title_entry = tk.Entry(content, font=F_BODY, bg="#FFFFFF", fg=INK, relief="flat", bd=0,
                               highlightthickness=1, highlightbackground=FIELD,
                               highlightcolor=ACCENT)
        title_entry.insert(0, book["title"])
        title_entry.pack(fill="x", ipady=8, pady=(4, 10))
        label(content, "Auteur", F_SMALL_B).pack(anchor="w")
        author_entry = tk.Entry(content, font=F_BODY, bg="#FFFFFF", fg=INK, relief="flat", bd=0,
                                highlightthickness=1, highlightbackground=FIELD,
                                highlightcolor=ACCENT)
        author_entry.insert(0, book["author"])
        author_entry.pack(fill="x", ipady=8, pady=(4, 6))
        label(content, f"L'ISBN reste inchangé : {book['isbnFormatted']}.", F_SMALL, MUTED).pack(
            anchor="w", pady=(4, 0))

        def commit():
            try:
                self.state = self.store.update_book(isbn, title_entry.get(), author_entry.get())
                self.close_dialog()
                self.toast("Livre modifié.")
                self.show(self.route)
            except ApiError as exc:
                self.toast(exc.message, "err")

        button(actions, "Enregistrer la modification", commit, "pri").pack(side="right")
        button(actions, "Annuler", self.close_dialog, "sec").pack(side="right", padx=(0, 8))

    def dialog_conflict(self, conflict):
        title = (f"Données incohérentes pour {conflict['userName']}"
                 if conflict["kind"] == "mismatch" else "Incohérence dans les données")
        top, content, actions = self._dialog(title, width=600)

        def resolve(keep):
            isbn = conflict["bookIsbn"] or conflict["userIsbn"]
            try:
                self.state = self.store.reconcile(conflict["userId"], isbn, keep)
                self.close_dialog()
                self.toast("Incohérence ignorée pour cette session." if keep == "ignore"
                           else "Incohérence corrigée.")
                self.show(self.route)
            except ApiError as exc:
                self.toast(exc.message, "err")

        if conflict["kind"] != "mismatch":
            label(content, self.conflict_text(conflict), F_SMALL, "#4A3E35", PAPER,
                  wraplength=520, justify="left").pack(anchor="w", pady=(0, 12))
            if conflict["kind"] == "missing_user":
                button(actions, "Rendre disponible",
                       lambda: resolve("return"), "pri").pack(side="right")
            else:
                button(actions, "Retirer de la liste",
                       lambda: resolve("drop"), "pri").pack(side="right")
            button(actions, "Ignorer", lambda: resolve("ignore"), "sec").pack(
                side="right", padx=(0, 8))
            return

        diff = tk.Frame(content, bg=PAPER)
        diff.pack(fill="x", pady=(0, 12))
        left = tk.Frame(diff, bg="#FFFFFF", highlightbackground=LINE, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        label(left, "books.txt dit", F_TINY, MUTED, "#FFFFFF").pack(anchor="w", padx=10, pady=(8, 2))
        label(left, f"{conflict['bookTitle']} emprunté par {conflict['userId']}", F_SMALL, INK,
              "#FFFFFF", wraplength=240, justify="left").pack(anchor="w", padx=10, pady=(0, 8))
        right = tk.Frame(diff, bg="#FFFFFF", highlightbackground=LINE, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))
        label(right, "users.txt dit", F_TINY, MUTED, "#FFFFFF").pack(anchor="w", padx=10, pady=(8, 2))
        label(right, f"{conflict['userId']} a emprunté {conflict['userTitle']}", F_SMALL, INK,
              "#FFFFFF", wraplength=240, justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        button(actions, f"Garder {conflict['bookTitle']}", lambda: resolve("book"),
               "pri").pack(side="right")
        button(actions, f"Garder {conflict['userTitle']}", lambda: resolve("user"),
               "sec").pack(side="right", padx=(0, 8))
        button(actions, "Ignorer", lambda: resolve("ignore"), "sec").pack(side="right", padx=(0, 8))

    # ------------------------------------------------------------- helpers
    def conflict_text(self, conflict):
        if conflict["kind"] == "missing_user":
            return f"« {conflict['bookTitle']} » est marqué emprunté par {conflict['userId']}, " \
                   "qui n'existe pas dans users.txt."
        if conflict["kind"] == "missing_book":
            return f"{conflict['userName']} ({conflict['userId']}) a « {conflict['userTitle']} » " \
                   "dans sa liste, mais ce livre n'existe pas dans books.txt."
        return f"« {conflict['bookTitle']} » est marqué emprunté par {conflict['userId']}, " \
               f"mais {conflict['userName']} a « {conflict['userTitle']} » dans sa liste."


def step_title(parent, number, text):
    row = tk.Frame(parent, bg=PAPER)
    row.pack(fill="x")
    circle = tk.Canvas(row, width=26, height=26, bg=PAPER, highlightthickness=0)
    circle.create_oval(0, 0, 26, 26, fill=INK, outline="")
    circle.create_text(13, 13, text=number, font=(SANS, 10, "bold"), fill=BG)
    circle.pack(side="left", padx=(0, 10))
    label(row, text, F_H2).pack(side="left")


# --------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser(description="Interface graphique de la bibliothèque")
    parser.add_argument("-d", "--data-dir", help="dossier contenant books.txt et users.txt")
    parser.add_argument("--selftest", action="store_true", help="construit les écrans puis quitte")
    parser.add_argument("--route", choices=["dashboard", "catalogue", "book", "loans", "users"],
                        help="écran à ouvrir au démarrage (captures, démonstration)")
    parser.add_argument("--isbn", help="ISBN pour l'écran fiche livre")
    args = parser.parse_args()

    store = Store(Path(args.data_dir) if args.data_dir else None)
    root = tk.Tk()
    app = App(root, store)
    if args.route:
        app.show(args.route, args.isbn)

    if args.selftest:
        for route in ("dashboard", "catalogue", "loans", "users"):
            app.show(route)
            root.update()
        app.loan_mode = "return"
        app.show("loans")
        root.update()
        if store.state()["books"]:
            app.show("book", store.state()["books"][1]["isbn"])
            root.update()
        root.destroy()
        print("selftest ok")
        return 0

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
