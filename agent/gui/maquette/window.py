"""Fenêtre principale, navigation et état global du prototype."""

from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from .components import (
    AddBookModal,
    AddUserModal,
    BorrowModal,
    ConfirmModal,
    Header,
    ReturnModal,
    Sidebar,
    Toast,
)
from .models import Book, LibraryStore, User
from .theme import COLORS, SPACING
from .views import (
    CatalogueView,
    DashboardView,
    DataBackupView,
    LoansView,
    PlaceholderView,
    StatisticsView,
    UsersView,
)


class LibraryApp(ctk.CTk):
    """Application de bibliothèque : maquette CustomTkinter."""

    HEADERS = {
        "Tableau de bord": (
            "Tableau de bord",
            "Vue d'ensemble de votre bibliothèque personnelle",
        ),
        "Catalogue": (
            "Catalogue",
            "Rechercher, ajouter ou retirer des ouvrages",
        ),
        "Utilisateurs": (
            "Utilisateurs",
            "Gérer les comptes et leurs emprunts",
        ),
        "Emprunts": (
            "Emprunts",
            "Suivre les prêts en cours et enregistrer les retours",
        ),
        "Statistiques": (
            "Statistiques",
            "Analyser la disponibilité de la collection",
        ),
        "Données & sauvegarde": (
            "Données & sauvegarde",
            "Consulter les fichiers source et simuler les sauvegardes",
        ),
    }

    def __init__(self):
        super().__init__()
        self.title("Bibliothèque — Maquette CustomTkinter")
        self.geometry("1280x800")
        self.minsize(1180, 720)
        self.configure(fg_color=COLORS["bg"])

        self.store = LibraryStore.load()
        self.current_screen = ""
        self._toast: Toast | None = None
        self.catalogue_query = ""
        self.catalogue_filter = CatalogueView.FILTERS[0]
        self.users_query = ""
        self.users_filter = UsersView.FILTERS[0]
        self.loans_query = ""
        self.loans_sort = LoansView.SORTS[0]
        self.last_simulated_action: dict | None = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, on_select=self.show_screen,
                               on_quit=self._confirm_quit)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.main = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.header = Header(top, *self.HEADERS["Tableau de bord"])
        self.header.grid(row=0, column=0, sticky="ew",
                         padx=SPACING["page_x"],
                         pady=(SPACING["page_y"], 14))
        ctk.CTkFrame(top, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=1, column=0, sticky="ew", padx=SPACING["page_x"])

        self.view_host = ctk.CTkFrame(self.main, fg_color=COLORS["bg"],
                                      corner_radius=0)
        self.view_host.grid(row=1, column=0, sticky="nsew")
        self.view_host.grid_rowconfigure(0, weight=1)
        self.view_host.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self._confirm_quit)
        self.show_screen("Tableau de bord")

    def show_screen(self, screen: str) -> None:
        self.current_screen = screen
        self.sidebar.set_active(screen)

        for child in self.view_host.winfo_children():
            child.destroy()

        if screen == "Tableau de bord":
            view = DashboardView(self.view_host, self)
        elif screen == "Catalogue":
            view = CatalogueView(self.view_host, self)
        elif screen == "Utilisateurs":
            view = UsersView(self.view_host, self)
        elif screen == "Emprunts":
            view = LoansView(self.view_host, self)
        elif screen == "Statistiques":
            view = StatisticsView(self.view_host, self)
        elif screen == "Données & sauvegarde":
            view = DataBackupView(self.view_host, self)
        else:
            view = PlaceholderView(self.view_host, self, screen)
        view.grid(row=0, column=0, sticky="nsew")

        title, subtitle = self.HEADERS.get(screen, (screen, ""))
        self.header.set_content(title, subtitle)

    def open_add_book(self) -> None:
        AddBookModal(self, self.store, on_done=self._after_change)

    def open_add_user(self) -> None:
        AddUserModal(self, self.store, on_done=self._after_change)

    def open_borrow(self, book: Book | None = None,
                    user: User | None = None) -> None:
        BorrowModal(self, self.store, on_done=self._after_change,
                    book=book, user=user)

    def open_return(self, book: Book | None = None) -> None:
        ReturnModal(self, self.store, on_done=self._after_change, book=book)

    def delete_book(self, book: Book) -> None:
        try:
            self.store.remove_book(book)
        except ValueError as exc:
            self.show_toast(str(exc), "error")
            return
        self.show_toast(f"« {book.title} » a été supprimé du catalogue.")
        self.show_screen(self.current_screen)

    def return_book(self, book: Book) -> None:
        try:
            self.store.return_book(book)
        except ValueError as exc:
            self.show_toast(str(exc), "error")
            return
        self.show_toast(f"« {book.title} » a été retourné.")
        self.show_screen(self.current_screen)

    def _after_change(self, message: str) -> None:
        self.show_toast(message)
        self.show_screen(self.current_screen)

    def show_toast(self, message: str, kind: str = "success") -> None:
        if self._toast is not None and self._toast.winfo_exists():
            self._toast.destroy()
        toast = Toast(self.main, message, kind)
        toast.place(relx=1.0, rely=1.0, x=-28, y=-22, anchor="se")
        toast.lift()
        self._toast = toast

        def _dismiss() -> None:
            if toast.winfo_exists():
                toast.destroy()

        self.after(3200, _dismiss)

    def simulate_data_action(self, action: str) -> None:
        now = datetime.now()
        if action == "backup":
            title = "Création d'une sauvegarde"
            detail = ("Des copies .backup de books.txt et users.txt "
                      "auraient été créées à côté des fichiers source.")
            toast = ("Création d'une sauvegarde simulée. Aucun fichier "
                     ".backup n'a été écrit.")
        else:
            title = "Sauvegarde des données"
            detail = ("Les livres et les utilisateurs en mémoire auraient "
                      "été enregistrés dans les fichiers source.")
            toast = ("Données sauvegardées (simulation). Aucun fichier "
                     "n'a été modifié.")
        self.last_simulated_action = {
            "action": action,
            "title": title,
            "detail": detail,
            "time": now,
        }
        self.show_screen(self.current_screen)
        self.show_toast(toast)

    def _confirm_quit(self) -> None:
        ConfirmModal(
            self,
            "Quitter l'application",
            "Les modifications non sauvegardées seront perdues. "
            "Voulez-vous fermer la maquette ?",
            confirm_text="Quitter",
            danger=True,
            on_confirm=self.destroy,
        )
