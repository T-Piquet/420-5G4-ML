"""Fenêtre unique CustomTkinter de la bibliothèque."""

from __future__ import annotations

import argparse
from pathlib import Path

import customtkinter as ctk

import theme
from data_store import LibraryStore, StoreError
from views import BooksView, UsersView


class LibraryApp(ctk.CTk):
    """Fenêtre principale et navigation entre les pages Livres et Utilisateurs."""

    def __init__(self, data_dir: Path) -> None:
        super().__init__(fg_color=theme.BACKGROUND)
        theme.init(self)
        self.store = LibraryStore(data_dir).load()
        self.title("Gestionnaire de la Bibliothèque")
        self.geometry("1000x700")
        self.minsize(900, 560)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._current_view: ctk.CTkFrame | None = None
        self._build_header()
        self.show_books()

    def _swap_view(self, view: ctk.CTkFrame) -> None:
        """Remplace la page courante par `view` dans la zone sous le bandeau."""
        if self._current_view is not None:
            self._current_view.destroy()
        self._current_view = view
        view.grid(row=1, column=0, sticky="nsew")

    def show_books(self) -> None:
        """Affiche la page Livres, écran principal."""
        self._swap_view(BooksView(self, self.store, self.show_users))

    def show_users(self) -> None:
        """Affiche la page Utilisateurs."""
        self._swap_view(UsersView(self, self.store, self.show_books))

    def _build_header(self) -> None:
        """Bandeau commun à toutes les pages."""
        header = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=0,
            border_width=0,
            height=theme.HEADER_HEIGHT,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Gestionnaire de la Bibliothèque",
            font=theme.font(24, "bold"),
            text_color=theme.TEXT,
            anchor="center",
        ).grid(row=0, column=0, sticky="nsew")


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

    ctk.set_appearance_mode("light")

    try:
        app = LibraryApp(args.data_dir)
    except StoreError as exc:
        parser.error(str(exc))

    app.mainloop()


if __name__ == "__main__":
    main()
