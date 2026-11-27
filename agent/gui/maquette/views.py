"""Écrans de la maquette. Le tableau de bord est l'écran d'accueil."""

from __future__ import annotations

from tkinter import StringVar

import customtkinter as ctk

from .components import ActionCard, Badge, Card, ConfirmModal, StatCard
from .models import Book, User
from .theme import COLORS, FONTS, SPACING


def _shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else f"{text[:limit - 1]}…"


class DashboardView(ctk.CTkScrollableFrame):
    """Tableau de bord : statistiques, actions rapides et emprunts en cours."""

    def __init__(self, master, app):
        super().__init__(
            master, fg_color=COLORS["bg"], corner_radius=0,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["text_soft"])
        self.app = app
        self.store = app.store
        self.grid_columnconfigure(0, weight=1)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=0, column=0, sticky="nsew",
                  padx=SPACING["page_x"], pady=(0, 12))
        body.grid_columnconfigure(0, weight=1)

        self._build_stats(body)
        self._build_lower(body)

    def _build_stats(self, parent) -> None:
        stats = ctk.CTkFrame(parent, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew")
        for column in range(4):
            stats.grid_columnconfigure(column, weight=1, uniform="stats")

        cards = (
            ("Livres au total", str(self.store.total_books),
             "ouvrages au catalogue", "▤",
             COLORS["accent"], COLORS["accent_soft"]),
            ("Disponibles", str(self.store.available_count),
             "prêts possibles", "✓",
             COLORS["success"], COLORS["success_soft"]),
            ("Empruntés", str(self.store.borrowed_count),
             "prêts en cours", "↗",
             COLORS["warning"], COLORS["warning_soft"]),
            ("Utilisateurs", str(self.store.total_users),
             "comptes enregistrés", "◉",
             COLORS["purple"], COLORS["purple_soft"]),
        )
        for index, (label, value, hint, symbol, accent, soft) in enumerate(cards):
            card = StatCard(stats, label, value, hint, symbol, accent, soft)
            card.grid(row=0, column=index, sticky="nsew", padx=8)

    def _build_lower(self, parent) -> None:
        lower = ctk.CTkFrame(parent, fg_color="transparent")
        lower.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        lower.grid_columnconfigure(0, weight=4)
        lower.grid_columnconfigure(1, weight=6)

        self._build_actions(lower).grid(row=0, column=0, sticky="nsew",
                                        padx=(0, 8))
        self._build_loans(lower).grid(row=0, column=1, sticky="nsew",
                                      padx=(8, 0))

    def _build_actions(self, parent) -> Card:
        card = Card(parent)
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 12))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Actions rapides", font=FONTS["title"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Les gestes du quotidien",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w", pady=(1, 0))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        for column in range(2):
            actions.grid_columnconfigure(column, weight=1, uniform="actions")
        for row in range(2):
            actions.grid_rowconfigure(row, weight=1, uniform="actions")

        cards = (
            ("Ajouter un livre", "Enrichir le catalogue", "+",
             COLORS["accent"], COLORS["accent_soft"], self.app.open_add_book),
            ("Ajouter un utilisateur", "Créer un compte", "◉",
             COLORS["purple"], COLORS["purple_soft"], self.app.open_add_user),
            ("Emprunter un livre", "Enregistrer un prêt", "→",
             COLORS["warning"], COLORS["warning_soft"], self.app.open_borrow),
            ("Retourner un livre", "Clôturer un prêt", "←",
             COLORS["success"], COLORS["success_soft"], self.app.open_return),
        )
        for index, (title, subtitle, symbol, accent, soft, command) in enumerate(cards):
            action = ActionCard(actions, title, subtitle, symbol, accent, soft,
                                command)
            action.grid(row=index // 2, column=index % 2, sticky="nsew",
                        padx=5, pady=5)
        return card

    def _build_loans(self, parent) -> Card:
        card = Card(parent)
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Emprunts en cours", font=FONTS["title"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Les ouvrages actuellement sortis",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w", pady=(1, 0))

        count = Badge(header, f"{self.store.borrowed_count} prêt(s)",
                      COLORS["warning_soft"], COLORS["warning"])
        count.grid(row=0, column=1, rowspan=2, sticky="e")

        rows = ctk.CTkFrame(card, fg_color="transparent")
        rows.grid(row=1, column=0, sticky="nsew", padx=20)
        rows.grid_columnconfigure(0, weight=1)
        rows.grid_columnconfigure(1, minsize=120)
        rows.grid_columnconfigure(2, minsize=80)
        rows.grid_columnconfigure(3, minsize=74)

        for column, title in enumerate(("LIVRE", "EMPRUNTEUR", "STATUT", "")):
            ctk.CTkLabel(rows, text=title, font=FONTS["caption"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=0, column=column, sticky="w", pady=(4, 2))

        loans = self.store.ongoing_loans()
        visible = loans[:4]
        if not loans:
            self._build_empty_loans(rows)
        else:
            for index, (book, user) in enumerate(visible):
                self._build_loan_row(rows, index * 2 + 1, book, user)
            if len(loans) > len(visible):
                ctk.CTkLabel(
                    rows,
                    text=f"… et {len(loans) - len(visible)} autre(s) emprunt(s)",
                    font=FONTS["body_small"],
                    text_color=COLORS["text_soft"], anchor="w").grid(
                    row=len(visible) * 2 + 1, column=0, columnspan=4,
                    sticky="w", pady=(8, 0))

        self._build_availability(card)
        return card

    def _build_loan_row(self, rows, row: int, book: Book, user) -> None:
        book_cell = ctk.CTkFrame(rows, fg_color="transparent")
        book_cell.grid(row=row, column=0, sticky="ew", pady=(9, 0),
                       padx=(0, 10))
        book_cell.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(book_cell, text=_shorten(book.title, 21),
                     font=FONTS["body_bold"], text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(book_cell, text=_shorten(book.author, 28),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w")

        borrower = ctk.CTkFrame(rows, fg_color="transparent")
        borrower.grid(row=row, column=1, sticky="w", pady=(9, 0))
        name = user.name if user else "Emprunteur inconnu"
        identifier = user.user_id if user else book.borrower_id or "—"
        ctk.CTkLabel(borrower, text=_shorten(name, 18), font=FONTS["body"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(borrower, text=identifier, font=FONTS["body_small"],
                     text_color=COLORS["text_soft"], anchor="w").grid(
            row=1, column=0, sticky="w")

        status = ctk.CTkFrame(rows, fg_color="transparent")
        status.grid(row=row, column=2, sticky="w", pady=(9, 0))
        Badge(status, "Emprunté", COLORS["warning_soft"],
              COLORS["warning"]).grid(sticky="w")

        ctk.CTkButton(
            rows, text="Retour", width=72, height=28, corner_radius=8,
            fg_color=COLORS["accent_soft"], hover_color=COLORS["accent"],
            text_color=COLORS["accent"], font=FONTS["body_small"],
            command=lambda b=book: self.app.return_book(b)).grid(
            row=row, column=3, sticky="w", pady=(9, 0))

        ctk.CTkFrame(rows, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=row + 1, column=0, columnspan=4, sticky="ew", pady=(9, 0))

    def _build_empty_loans(self, rows) -> None:
        empty = ctk.CTkFrame(rows, fg_color="transparent")
        empty.grid(row=1, column=0, columnspan=4, sticky="ew", pady=28)
        empty.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(empty, text="✓", font=FONTS["icon_large"],
                     text_color=COLORS["success"]).grid(row=0, column=0)
        ctk.CTkLabel(empty, text="Aucun emprunt en cours",
                     font=FONTS["body_bold"],
                     text_color=COLORS["text"]).grid(row=1, column=0,
                                                     pady=(4, 0))
        ctk.CTkLabel(empty, text="Tous les ouvrages sont disponibles.",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).grid(row=2, column=0)

    def _build_availability(self, card) -> None:
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(14, 18))
        footer.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(footer, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Taux de disponibilité",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(top, text=f"{self.store.availability_rate} %",
                     font=FONTS["body_bold"],
                     text_color=COLORS["success"], anchor="e").grid(
            row=0, column=1, sticky="e")

        progress = ctk.CTkProgressBar(
            footer, height=8, corner_radius=4,
            fg_color=COLORS["surface_alt"],
            progress_color=COLORS["success"])
        progress.grid(row=1, column=0, sticky="ew", pady=(7, 0))
        progress.set(self.store.availability_rate / 100)


class CatalogueView(ctk.CTkFrame):
    """Catalogue : recherche, filtres et gestion des ouvrages."""

    FILTERS = ("Tous", "Disponibles", "Empruntés")

    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.app = app
        self.store = app.store
        self.query = getattr(app, "catalogue_query", "")
        self.filter = getattr(app, "catalogue_filter", self.FILTERS[0])
        if self.filter not in self.FILTERS:
            self.filter = self.FILTERS[0]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_table()
        self._refresh()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew",
                     padx=SPACING["page_x"], pady=(0, 14))
        toolbar.grid_columnconfigure(0, weight=1)

        search = ctk.CTkFrame(toolbar, fg_color=COLORS["surface"],
                              corner_radius=10, border_width=1,
                              border_color=COLORS["border"], height=42)
        search.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        search.grid_propagate(False)
        search.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search, text="⌕", font=FONTS["icon_small"],
                     text_color=COLORS["text_soft"]).grid(
            row=0, column=0, padx=(12, 6))
        self.search_var = StringVar(value=self.query)
        self.search_entry = ctk.CTkEntry(
            search, textvariable=self.search_var, height=38,
            border_width=0, fg_color=COLORS["surface"],
            text_color=COLORS["text"], font=FONTS["body"],
            placeholder_text="Rechercher par titre ou auteur…",
            placeholder_text_color=COLORS["text_soft"])
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_var.trace_add("write", self._on_search)

        self.filter_var = StringVar(value=self.filter)
        self.filter_menu = ctk.CTkSegmentedButton(
            toolbar, values=list(self.FILTERS), variable=self.filter_var,
            command=self._on_filter, height=42, corner_radius=10,
            font=FONTS["body"], text_color=COLORS["text_muted"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"])
        self.filter_menu.grid(row=0, column=1, padx=(0, 12))

        ctk.CTkButton(
            toolbar, text="+  Ajouter un livre", height=42, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF", font=FONTS["body_bold"],
            command=self.app.open_add_book).grid(row=0, column=2)

    def _build_table(self) -> None:
        card = Card(self)
        card.grid(row=1, column=0, sticky="nsew",
                  padx=SPACING["page_x"], pady=(0, SPACING["page_y"]))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Liste des ouvrages", font=FONTS["title"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Recherchez, filtrez et gérez la collection",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w", pady=(1, 0))

        self.count_badge = Badge(header, "", COLORS["accent_soft"],
                                 COLORS["accent"])
        self.count_badge.grid(row=0, column=1, rowspan=2, sticky="e")

        columns = ctk.CTkFrame(card, fg_color="transparent")
        columns.grid(row=1, column=0, sticky="ew", padx=(20, 34))
        self._configure_columns(columns)
        for index, title in enumerate(("LIVRE", "ISBN", "STATUT", "ACTIONS")):
            ctk.CTkLabel(columns, text=title, font=FONTS["caption"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=0, column=index, sticky="w", pady=(4, 6))
        ctk.CTkFrame(columns, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=1, column=0, columnspan=4, sticky="ew")

        self.rows = ctk.CTkScrollableFrame(
            card, fg_color=COLORS["surface"], corner_radius=0,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["text_soft"])
        self.rows.grid(row=2, column=0, sticky="nsew", padx=(20, 14),
                       pady=(0, 16))
        self._configure_columns(self.rows)

    @staticmethod
    def _configure_columns(frame) -> None:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, minsize=132)
        frame.grid_columnconfigure(2, minsize=112)
        frame.grid_columnconfigure(3, minsize=196)

    def _refresh(self) -> None:
        for child in self.rows.winfo_children():
            child.destroy()
        books = self._visible_books()
        self.count_badge.set_text(f"{len(books)} ouvrage(s)")
        if not books:
            self._build_empty()
            return
        for index, book in enumerate(books):
            self._build_row(index * 2, book)

    def _build_empty(self) -> None:
        empty = ctk.CTkFrame(self.rows, fg_color="transparent")
        empty.grid(row=0, column=0, columnspan=4, sticky="ew", pady=56)
        empty.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(empty, text="⌕", font=FONTS["icon_large"],
                     text_color=COLORS["text_soft"]).grid(row=0, column=0)
        if self.query.strip():
            title = "Aucun livre ne correspond à votre recherche"
            hint = "Modifiez le titre ou l'auteur recherché."
        else:
            title = "Aucun livre dans cette catégorie"
            hint = "Changez de filtre ou ajoutez un nouvel ouvrage."
        ctk.CTkLabel(empty, text=title, font=FONTS["body_bold"],
                     text_color=COLORS["text"]).grid(row=1, column=0,
                                                     pady=(4, 0))
        ctk.CTkLabel(empty, text=hint, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).grid(row=2, column=0,
                                                           pady=(2, 0))

    def _build_row(self, row: int, book: Book) -> None:
        title_cell = ctk.CTkFrame(self.rows, fg_color="transparent")
        title_cell.grid(row=row, column=0, sticky="ew", padx=(0, 12),
                        pady=(10, 0))
        title_cell.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_cell, text=_shorten(book.title, 46),
                     font=FONTS["body_bold"], text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_cell, text=_shorten(book.author, 50),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w")

        ctk.CTkLabel(self.rows, text=book.isbn, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=row, column=1, sticky="w", pady=(10, 0))

        status = ctk.CTkFrame(self.rows, fg_color="transparent")
        status.grid(row=row, column=2, sticky="w", pady=(10, 0))
        if book.available:
            Badge(status, "Disponible", COLORS["success_soft"],
                  COLORS["success"]).grid(sticky="w")
        else:
            Badge(status, "Emprunté", COLORS["warning_soft"],
                  COLORS["warning"]).grid(sticky="w")
            borrower = self.store.user_for(book)
            name = borrower.name if borrower else book.borrower_id or "—"
            ctk.CTkLabel(status, text=_shorten(name, 20),
                         font=FONTS["body_small"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=1, column=0, sticky="w", pady=(2, 0))

        actions = ctk.CTkFrame(self.rows, fg_color="transparent")
        actions.grid(row=row, column=3, sticky="w", pady=(10, 0))
        if book.available:
            ctk.CTkButton(
                actions, text="Emprunter", width=92, height=30,
                corner_radius=8, fg_color=COLORS["accent_soft"],
                hover_color=COLORS["accent"], text_color=COLORS["accent"],
                font=FONTS["body_small"],
                command=lambda b=book: self.app.open_borrow(b)).grid(
                row=0, column=0, padx=(0, 8))
        else:
            ctk.CTkButton(
                actions, text="Retour", width=92, height=30, corner_radius=8,
                fg_color=COLORS["accent_soft"], hover_color=COLORS["accent"],
                text_color=COLORS["accent"], font=FONTS["body_small"],
                command=lambda b=book: self.app.open_return(b)).grid(
                row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            actions, text="Supprimer", width=88, height=30, corner_radius=8,
            fg_color=COLORS["danger_soft"], hover_color="#FECACA",
            text_color=COLORS["danger"], font=FONTS["body_small"],
            command=lambda b=book: self._confirm_delete(b)).grid(
            row=0, column=1)

        ctk.CTkFrame(self.rows, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=row + 1, column=0, columnspan=4, sticky="ew", pady=(10, 0))

    def _visible_books(self) -> list[Book]:
        books = list(self.store.books)
        if self.filter == "Disponibles":
            books = [book for book in books if book.available]
        elif self.filter == "Empruntés":
            books = [book for book in books if not book.available]
        query = self.query.strip().casefold()
        if query:
            books = [book for book in books
                     if query in book.title.casefold()
                     or query in book.author.casefold()]
        return books

    def _on_search(self, *_args) -> None:
        self.query = self.search_var.get()
        self.app.catalogue_query = self.query
        self._refresh()

    def _on_filter(self, value: str) -> None:
        self.filter = value
        self.app.catalogue_filter = value
        self._refresh()

    def _confirm_delete(self, book: Book) -> None:
        message = f"« {book.title} » sera définitivement retiré du catalogue."
        if not book.available:
            borrower = self.store.user_for(book)
            name = borrower.name if borrower else "l'emprunteur"
            message += (f" L'emprunt en cours de {name} sera clôturé et le "
                        "livre retiré de son compte.")
        ConfirmModal(
            self.app, "Supprimer un livre", message,
            confirm_text="Supprimer", danger=True,
            on_confirm=lambda: self.app.delete_book(book))


class UsersView(ctk.CTkFrame):
    """Utilisateurs : recherche, filtres et gestion des comptes emprunteurs."""

    FILTERS = ("Tous", "Avec emprunts", "Sans emprunt")

    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.app = app
        self.store = app.store
        self.query = getattr(app, "users_query", "")
        self.filter = getattr(app, "users_filter", self.FILTERS[0])
        if self.filter not in self.FILTERS:
            self.filter = self.FILTERS[0]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_table()
        self._refresh()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew",
                     padx=SPACING["page_x"], pady=(0, 14))
        toolbar.grid_columnconfigure(0, weight=1)

        search = ctk.CTkFrame(toolbar, fg_color=COLORS["surface"],
                              corner_radius=10, border_width=1,
                              border_color=COLORS["border"], height=42)
        search.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        search.grid_propagate(False)
        search.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search, text="⌕", font=FONTS["icon_small"],
                     text_color=COLORS["text_soft"]).grid(
            row=0, column=0, padx=(12, 6))
        self.search_var = StringVar(value=self.query)
        self.search_entry = ctk.CTkEntry(
            search, textvariable=self.search_var, height=38,
            border_width=0, fg_color=COLORS["surface"],
            text_color=COLORS["text"], font=FONTS["body"],
            placeholder_text="Rechercher par nom ou identifiant…",
            placeholder_text_color=COLORS["text_soft"])
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_var.trace_add("write", self._on_search)

        self.filter_var = StringVar(value=self.filter)
        self.filter_menu = ctk.CTkSegmentedButton(
            toolbar, values=list(self.FILTERS), variable=self.filter_var,
            command=self._on_filter, height=42, corner_radius=10,
            font=FONTS["body"], text_color=COLORS["text_muted"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"])
        self.filter_menu.grid(row=0, column=1, padx=(0, 12))

        ctk.CTkButton(
            toolbar, text="+  Ajouter un utilisateur", height=42,
            corner_radius=10, fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], text_color="#FFFFFF",
            font=FONTS["body_bold"],
            command=self.app.open_add_user).grid(row=0, column=2)

    def _build_table(self) -> None:
        card = Card(self)
        card.grid(row=1, column=0, sticky="nsew",
                  padx=SPACING["page_x"], pady=(0, SPACING["page_y"]))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Liste des utilisateurs",
                     font=FONTS["title"], text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Suivez les comptes et leurs emprunts",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w", pady=(1, 0))

        self.count_badge = Badge(header, "", COLORS["purple_soft"],
                                 COLORS["purple"])
        self.count_badge.grid(row=0, column=1, rowspan=2, sticky="e")

        columns = ctk.CTkFrame(card, fg_color="transparent")
        columns.grid(row=1, column=0, sticky="ew", padx=(20, 34))
        self._configure_columns(columns)
        for index, title in enumerate(("UTILISATEUR", "IDENTIFIANT",
                                       "EMPRUNTS", "ACTIONS")):
            ctk.CTkLabel(columns, text=title, font=FONTS["caption"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=0, column=index, sticky="w", pady=(4, 6))
        ctk.CTkFrame(columns, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=1, column=0, columnspan=4, sticky="ew")

        self.rows = ctk.CTkScrollableFrame(
            card, fg_color=COLORS["surface"], corner_radius=0,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["text_soft"])
        self.rows.grid(row=2, column=0, sticky="nsew", padx=(20, 14),
                       pady=(0, 16))
        self._configure_columns(self.rows)

    @staticmethod
    def _configure_columns(frame) -> None:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, minsize=112)
        frame.grid_columnconfigure(2, minsize=270)
        frame.grid_columnconfigure(3, minsize=118)

    def _refresh(self) -> None:
        for child in self.rows.winfo_children():
            child.destroy()
        users = self._visible_users()
        count = len(users)
        self.count_badge.set_text(
            f"{count} compte" if count == 1 else f"{count} comptes")
        if not users:
            self._build_empty()
            return
        for index, user in enumerate(users):
            self._build_row(index * 2, user)

    def _build_empty(self) -> None:
        empty = ctk.CTkFrame(self.rows, fg_color="transparent")
        empty.grid(row=0, column=0, columnspan=4, sticky="ew", pady=56)
        empty.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(empty, text="◉", font=FONTS["icon_large"],
                     text_color=COLORS["text_soft"]).grid(row=0, column=0)
        if self.query.strip():
            title = "Aucun utilisateur ne correspond à votre recherche"
            hint = "Modifiez le nom ou l'identifiant recherché."
        else:
            title = "Aucun utilisateur dans cette catégorie"
            hint = "Changez de filtre ou créez un nouveau compte."
        ctk.CTkLabel(empty, text=title, font=FONTS["body_bold"],
                     text_color=COLORS["text"]).grid(row=1, column=0,
                                                     pady=(4, 0))
        ctk.CTkLabel(empty, text=hint, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).grid(row=2, column=0,
                                                           pady=(2, 0))

    def _build_row(self, row: int, user) -> None:
        identity = ctk.CTkFrame(self.rows, fg_color="transparent")
        identity.grid(row=row, column=0, sticky="ew", padx=(0, 12),
                      pady=(10, 0))
        identity.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(identity, width=38, height=38, corner_radius=19,
                              fg_color=COLORS["accent_soft"])
        avatar.grid_propagate(False)
        avatar.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        ctk.CTkLabel(avatar, text=(user.name[:1].upper() or "?"),
                     font=FONTS["body_bold"],
                     text_color=COLORS["accent"]).place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(identity, text=_shorten(user.name, 30),
                     font=FONTS["body_bold"], text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=1, sticky="w")
        count = len(user.borrowed_isbns)
        if count == 0:
            subtitle = "Aucun emprunt en cours"
        elif count == 1:
            subtitle = "1 emprunt en cours"
        else:
            subtitle = f"{count} emprunts en cours"
        ctk.CTkLabel(identity, text=subtitle, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=1, sticky="w")

        ctk.CTkLabel(self.rows, text=user.user_id, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=row, column=1, sticky="w", pady=(10, 0))

        loans = ctk.CTkFrame(self.rows, fg_color="transparent")
        loans.grid(row=row, column=2, sticky="w", pady=(10, 0))
        if count:
            label = f"{count} emprunt" if count == 1 else f"{count} emprunts"
            Badge(loans, label, COLORS["warning_soft"],
                  COLORS["warning"]).grid(row=0, column=0, sticky="w")
            titles = []
            for isbn in user.borrowed_isbns:
                book = self.store.book_by_isbn(isbn)
                titles.append(book.title if book else isbn)
            ctk.CTkLabel(loans, text=_shorten(" · ".join(titles), 46),
                         font=FONTS["body_small"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=1, column=0, sticky="w", pady=(3, 0))
        else:
            ctk.CTkLabel(loans, text="Aucun emprunt",
                         font=FONTS["body_small"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=0, column=0, sticky="w")

        actions = ctk.CTkFrame(self.rows, fg_color="transparent")
        actions.grid(row=row, column=3, sticky="w", pady=(10, 0))
        ctk.CTkButton(
            actions, text="Emprunter", width=104, height=30,
            corner_radius=8, fg_color=COLORS["accent_soft"],
            hover_color=COLORS["accent"], text_color=COLORS["accent"],
            font=FONTS["body_small"],
            command=lambda u=user: self.app.open_borrow(user=u)).grid()

        ctk.CTkFrame(self.rows, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=row + 1, column=0, columnspan=4, sticky="ew", pady=(10, 0))

    def _visible_users(self):
        users = list(self.store.users)
        if self.filter == "Avec emprunts":
            users = [user for user in users if user.borrowed_isbns]
        elif self.filter == "Sans emprunt":
            users = [user for user in users if not user.borrowed_isbns]
        query = self.query.strip().casefold()
        if query:
            users = [user for user in users
                     if query in user.name.casefold()
                     or query in user.user_id.casefold()]
        return users

    def _on_search(self, *_args) -> None:
        self.query = self.search_var.get()
        self.app.users_query = self.query
        self._refresh()

    def _on_filter(self, value: str) -> None:
        self.filter = value
        self.app.users_filter = value
        self._refresh()


class LoansView(ctk.CTkFrame):
    """Emprunts : suivi des prêts en cours et retours rapides."""

    SORTS = ("Titre", "Emprunteur", "ISBN")

    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.app = app
        self.store = app.store
        self.query = getattr(app, "loans_query", "")
        self.sort = getattr(app, "loans_sort", self.SORTS[0])
        if self.sort not in self.SORTS:
            self.sort = self.SORTS[0]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_table()
        self._refresh()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew",
                     padx=SPACING["page_x"], pady=(0, 14))
        toolbar.grid_columnconfigure(0, weight=1)

        search = ctk.CTkFrame(toolbar, fg_color=COLORS["surface"],
                              corner_radius=10, border_width=1,
                              border_color=COLORS["border"], height=42)
        search.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        search.grid_propagate(False)
        search.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search, text="⌕", font=FONTS["icon_small"],
                     text_color=COLORS["text_soft"]).grid(
            row=0, column=0, padx=(12, 6))
        self.search_var = StringVar(value=self.query)
        self.search_entry = ctk.CTkEntry(
            search, textvariable=self.search_var, height=38,
            border_width=0, fg_color=COLORS["surface"],
            text_color=COLORS["text"], font=FONTS["body"],
            placeholder_text="Rechercher un livre ou un emprunteur…",
            placeholder_text_color=COLORS["text_soft"])
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_var.trace_add("write", self._on_search)

        self.sort_var = StringVar(value=self.sort)
        self.sort_menu = ctk.CTkSegmentedButton(
            toolbar, values=list(self.SORTS), variable=self.sort_var,
            command=self._on_sort, height=42, corner_radius=10,
            font=FONTS["body"], text_color=COLORS["text_muted"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"])
        self.sort_menu.grid(row=0, column=1, padx=(0, 12))

        ctk.CTkButton(
            toolbar, text="+  Emprunter un livre", height=42, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF", font=FONTS["body_bold"],
            command=self.app.open_borrow).grid(row=0, column=2)

    def _build_table(self) -> None:
        card = Card(self)
        card.grid(row=1, column=0, sticky="nsew",
                  padx=SPACING["page_x"], pady=(0, SPACING["page_y"]))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Emprunts en cours", font=FONTS["title"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Clôturez les prêts dès le retour des ouvrages",
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w", pady=(1, 0))

        badges = ctk.CTkFrame(header, fg_color="transparent")
        badges.grid(row=0, column=1, rowspan=2, sticky="e")
        self.borrowers_badge = Badge(badges, "", COLORS["accent_soft"],
                                     COLORS["accent"])
        self.borrowers_badge.grid(row=0, column=0, padx=(0, 8))
        self.count_badge = Badge(badges, "", COLORS["warning_soft"],
                                 COLORS["warning"])
        self.count_badge.grid(row=0, column=1)

        columns = ctk.CTkFrame(card, fg_color="transparent")
        columns.grid(row=1, column=0, sticky="ew", padx=(20, 34))
        self._configure_columns(columns)
        for index, title in enumerate(("LIVRE", "EMPRUNTEUR", "ISBN",
                                       "ACTIONS")):
            ctk.CTkLabel(columns, text=title, font=FONTS["caption"],
                         text_color=COLORS["text_soft"], anchor="w").grid(
                row=0, column=index, sticky="w", pady=(4, 6))
        ctk.CTkFrame(columns, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=1, column=0, columnspan=4, sticky="ew")

        self.rows = ctk.CTkScrollableFrame(
            card, fg_color=COLORS["surface"], corner_radius=0,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["text_soft"])
        self.rows.grid(row=2, column=0, sticky="nsew", padx=(20, 14),
                       pady=(0, 16))
        self._configure_columns(self.rows)

    @staticmethod
    def _configure_columns(frame) -> None:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, minsize=210)
        frame.grid_columnconfigure(2, minsize=136)
        frame.grid_columnconfigure(3, minsize=96)

    def _refresh(self) -> None:
        for child in self.rows.winfo_children():
            child.destroy()
        loans = self._visible_loans()
        count = len(loans)
        self.count_badge.set_text(
            f"{count} emprunt" if count == 1 else f"{count} emprunts")
        borrowers = {user.user_id for _book, user in loans if user is not None}
        self.borrowers_badge.set_text(
            f"{len(borrowers)} emprunteur"
            if len(borrowers) == 1 else f"{len(borrowers)} emprunteurs")
        if not loans:
            self._build_empty()
            return
        for index, (book, user) in enumerate(loans):
            self._build_row(index * 2, book, user)

    def _build_empty(self) -> None:
        empty = ctk.CTkFrame(self.rows, fg_color="transparent")
        empty.grid(row=0, column=0, columnspan=4, sticky="ew", pady=56)
        empty.grid_columnconfigure(0, weight=1)

        if self.query.strip():
            symbol = "⌕"
            color = COLORS["text_soft"]
            title = "Aucun emprunt ne correspond à votre recherche"
            hint = "Modifiez le titre, l'auteur, l'ISBN ou l'emprunteur."
        else:
            symbol = "✓"
            color = COLORS["success"]
            title = "Aucun emprunt en cours"
            hint = "Tous les ouvrages sont disponibles au prêt."
        ctk.CTkLabel(empty, text=symbol, font=FONTS["icon_large"],
                     text_color=color).grid(row=0, column=0)
        ctk.CTkLabel(empty, text=title, font=FONTS["body_bold"],
                     text_color=COLORS["text"]).grid(row=1, column=0,
                                                     pady=(4, 0))
        ctk.CTkLabel(empty, text=hint, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).grid(row=2, column=0,
                                                           pady=(2, 0))
        if not self.query.strip() and self.store.available_books():
            ctk.CTkButton(
                empty, text="Emprunter un livre", height=36, width=170,
                corner_radius=9, fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"], text_color="#FFFFFF",
                font=FONTS["body_bold"],
                command=self.app.open_borrow).grid(row=3, column=0,
                                                   pady=(16, 0))

    def _build_row(self, row: int, book: Book, user) -> None:
        book_cell = ctk.CTkFrame(self.rows, fg_color="transparent")
        book_cell.grid(row=row, column=0, sticky="ew", padx=(0, 12),
                       pady=(10, 0))
        book_cell.grid_columnconfigure(1, weight=1)

        icon = ctk.CTkFrame(book_cell, width=36, height=36, corner_radius=10,
                            fg_color=COLORS["warning_soft"])
        icon.grid_propagate(False)
        icon.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        ctk.CTkLabel(icon, text="▤", font=FONTS["icon"],
                     text_color=COLORS["warning"]).place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(book_cell, text=_shorten(book.title, 42),
                     font=FONTS["body_bold"], text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(book_cell, text=_shorten(book.author, 48),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=1, sticky="w")

        borrower = ctk.CTkFrame(self.rows, fg_color="transparent")
        borrower.grid(row=row, column=1, sticky="w", pady=(10, 0))
        name = user.name if user else "Emprunteur inconnu"
        identifier = user.user_id if user else (book.borrower_id or "—")
        ctk.CTkLabel(borrower, text=_shorten(name, 24),
                     font=FONTS["body"], text_color=COLORS["text"],
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(borrower, text=identifier, font=FONTS["body_small"],
                     text_color=COLORS["text_soft"], anchor="w").grid(
            row=1, column=0, sticky="w")

        ctk.CTkLabel(self.rows, text=book.isbn, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=row, column=2, sticky="w", pady=(10, 0))

        ctk.CTkButton(
            self.rows, text="Retour", width=82, height=30, corner_radius=8,
            fg_color=COLORS["accent_soft"], hover_color=COLORS["accent"],
            text_color=COLORS["accent"], font=FONTS["body_small"],
            command=lambda b=book: self.app.return_book(b)).grid(
            row=row, column=3, sticky="w", pady=(10, 0))

        ctk.CTkFrame(self.rows, height=1, corner_radius=0,
                     fg_color=COLORS["border"]).grid(
            row=row + 1, column=0, columnspan=4, sticky="ew", pady=(10, 0))

    def _visible_loans(self) -> list[tuple[Book, User | None]]:
        loans = self.store.ongoing_loans()
        query = self.query.strip().casefold()
        if query:
            filtered = []
            for book, user in loans:
                borrower = user.name if user else book.borrower_id
                haystack = " ".join((
                    book.title, book.author, book.isbn, book.borrower_id,
                    borrower)).casefold()
                if query in haystack:
                    filtered.append((book, user))
            loans = filtered
        if self.sort == "Emprunteur":
            loans.sort(key=lambda loan: (
                loan[1].name.casefold() if loan[1] else "zzz",
                loan[0].title.casefold()))
        elif self.sort == "ISBN":
            loans.sort(key=lambda loan: loan[0].isbn)
        else:
            loans.sort(key=lambda loan: loan[0].title.casefold())
        return loans

    def _on_search(self, *_args) -> None:
        self.query = self.search_var.get()
        self.app.loans_query = self.query
        self._refresh()

    def _on_sort(self, value: str) -> None:
        self.sort = value
        self.app.loans_sort = value
        self._refresh()


class PlaceholderView(ctk.CTkFrame):
    """Écran temporaire pour les modules pas encore maquettés."""

    def __init__(self, master, app, screen: str):
        super().__init__(master, fg_color=COLORS["bg"], corner_radius=0)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = Card(self, width=560, height=300)
        card.grid_propagate(False)
        card.grid(row=0, column=0)
        card.grid_columnconfigure(0, weight=1)

        icon = ctk.CTkFrame(card, width=64, height=64, corner_radius=18,
                            fg_color=COLORS["accent_soft"])
        icon.grid_propagate(False)
        icon.grid(row=0, column=0, pady=(40, 0))
        ctk.CTkLabel(icon, text="▤", font=FONTS["icon_large"],
                     text_color=COLORS["accent"]).place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=screen, font=FONTS["display"],
                     text_color=COLORS["text"]).grid(row=1, column=0,
                                                     pady=(16, 4))
        ctk.CTkLabel(
            card,
            text="Cet écran fait partie de la maquette et sera ajouté "
                 "dans une prochaine étape.",
            font=FONTS["body"], text_color=COLORS["text_muted"],
            wraplength=420, justify="center").grid(row=2, column=0)

        ctk.CTkButton(
            card, text="Retour au tableau de bord", height=40, width=210,
            corner_radius=10, fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], text_color="#FFFFFF",
            font=FONTS["body_bold"],
            command=lambda: self.app.show_screen("Tableau de bord")).grid(
            row=3, column=0, pady=(22, 0))
