"""Fenêtre unique CustomTkinter pour consulter et gérer la bibliothèque."""

from __future__ import annotations

import argparse
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from data_store import Book, LibraryStore, StoreError


class LibraryApp(ctk.CTk):
    def __init__(self, data_dir: Path) -> None:
        super().__init__()
        self.store = LibraryStore(data_dir).load()
        self.title("Bibliothèque personnelle")
        self.geometry("1000x700")
        self.minsize(780, 500)
        self.search_var = ctk.StringVar()
        self._build_layout()
        self._refresh_books()
        self._update_status()

    # ------------------------------------------------------------- interface
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            header, text="Ma bibliothèque", font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        self.theme_switch = ctk.CTkSwitch(
            header, text="Mode sombre", command=self._toggle_theme
        )
        self.theme_switch.grid(row=0, column=2, sticky="e")
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()

        search_bar = ctk.CTkFrame(self, fg_color="transparent")
        search_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=4)
        search_bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(search_bar, text="Rechercher").grid(row=0, column=0, sticky="w")
        self.search_entry = ctk.CTkEntry(
            search_bar, textvariable=self.search_var, placeholder_text="Titre ou auteur"
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=8)

        self.books_frame = ctk.CTkScrollableFrame(self, label_text="Livres")
        self.books_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=8)
        self.search_var.trace_add("write", lambda *_: self._refresh_books())

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 16))
        self.status_label = ctk.CTkLabel(footer, text="", anchor="e", text_color="gray")
        self.status_label.pack(side="right")

    def _refresh_books(self) -> None:
        for child in self.books_frame.winfo_children():
            child.destroy()

        books = self.store.search(self.search_var.get())
        if not books:
            ctk.CTkLabel(
                self.books_frame, text="Aucun livre trouvé.", text_color="gray"
            ).pack(pady=24)
            return

        for book in books:
            self._book_row(book)

    def _book_row(self, book: Book) -> None:
        row = ctk.CTkFrame(self.books_frame)
        row.pack(fill="x", padx=4, pady=4)
        row.grid_columnconfigure(0, weight=1)

        status = "Disponible" if book.available else f"Emprunté ({book.borrower_id})"
        text = f"{book.title} — {book.author}\nISBN {book.isbn} • {status}"
        ctk.CTkLabel(row, text=text, justify="left", anchor="w").grid(
            row=0, column=0, sticky="ew", padx=12, pady=8
        )

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkButton(
            actions,
            text="Supprimer",
            width=90,
            fg_color="#8b3a3a",
            hover_color="#6d2d2d",
            command=lambda b=book: self._delete_book(b),
        ).pack(side="left", padx=4)

    def _update_status(self, message: str = "") -> None:
        stats = self.store.stats
        text = (
            f"{stats['books']} livres • {stats['available']} disponibles • "
            f"{stats['borrowed']} empruntés • {stats['users']} utilisateurs"
        )
        if message:
            text = f"{message} — {text}"
        self.status_label.configure(text=text)

    def _commit(self, message: str) -> None:
        try:
            self.store.save()
        except OSError as exc:
            messagebox.showerror("Erreur de sauvegarde", str(exc))
            return
        self._refresh_books()
        self._update_status(message)

    def _toggle_theme(self) -> None:
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() else "Light")

    # ---------------------------------------------------------------- actions
    def _delete_book(self, book: Book) -> None:
        if not messagebox.askyesno("Supprimer", f"Supprimer « {book.title} » ?"):
            return
        try:
            self.store.remove_book(book.isbn)
        except StoreError as exc:
            messagebox.showerror("Suppression impossible", str(exc))
            return
        self._commit("Livre supprimé")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bibliothèque personnelle — interface graphique"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="répertoire contenant books.txt et users.txt (défaut : agent/data)",
    )
    args = parser.parse_args()

    if not args.data_dir.is_dir():
        parser.error(f"répertoire de données introuvable : {args.data_dir}")

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    try:
        app = LibraryApp(args.data_dir)
    except StoreError as exc:
        parser.error(str(exc))

    app.mainloop()


if __name__ == "__main__":
    main()
