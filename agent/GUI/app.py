"""Fenêtre unique CustomTkinter de la bibliothèque."""

from __future__ import annotations

import argparse
from pathlib import Path

import customtkinter as ctk

import theme
from data_store import LibraryStore, StoreError
from views import UsersView


class LibraryApp(ctk.CTk):
    """Fenêtre principale ; elle affiche pour l'instant la page Utilisateurs."""

    def __init__(self, data_dir: Path) -> None:
        super().__init__(fg_color=theme.BACKGROUND)
        theme.init(self)
        self.store = LibraryStore(data_dir).load()
        self.title("Bibliothèque personnelle")
        self.geometry("1000x700")
        self.minsize(900, 560)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        UsersView(self, self.store).grid(row=0, column=0, sticky="nsew")


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
