"""Fenetre principale de l'interface graphique de la bibliotheque."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "build"))
sys.path.insert(0, str(BASE_DIR / "python"))

import customtkinter as ctk

from service import LibraryService
from views.books import BooksView

APP_TITLE = "Gestion de bibliothèque"
TABS = ("Livres", "Utilisateurs", "Emprunts", "Statistiques")


class BibliothequeApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("900x600")
        self.minsize(700, 450)

        self.service = LibraryService()
        self.service.load()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="nsew")
        for name in TABS:
            self.tabview.add(name)

        self.status_var = ctk.StringVar(value=self._status_message())
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            anchor="w",
            height=28,
            corner_radius=6,
            fg_color=("gray85", "gray20"),
        )
        self.status_label.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        self.books_view = BooksView(
            self.tabview.tab("Livres"), self.service, self.set_status
        )
        self.books_view.pack(fill="both", expand=True, padx=8, pady=8)

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _status_message(self) -> str:
        stats = self.service.get_stats()
        return (
            f"{stats['total_books']} livres, {stats['total_users']} utilisateurs chargés"
        )


def main() -> None:
    app = BibliothequeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
