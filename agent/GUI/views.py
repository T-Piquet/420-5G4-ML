"""Vues de l'application : Livres (écran principal) et Utilisateurs."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import Event

import customtkinter as ctk

import theme
from data_store import Book, LibraryStore, StoreError, User
from panels import AddBookPanel, AddUserPanel, BorrowPanel

BOOK_COLUMNS = 3
USER_COLUMNS = 4

Command = Callable[[], None]


def _plural(count: int, singular: str, plural: str) -> str:
    """Accorde un nom avec son nombre (0 et 1 restent au singulier)."""
    return f"{count} {singular if count <= 1 else plural}"


def _borrowed_text(count: int) -> str:
    if count == 0:
        return "Aucun livre emprunté"
    return _plural(count, "livre emprunté", "livres empruntés")


def _draw_magnifier(canvas: tk.Canvas) -> None:
    """Dessine une loupe discrète dans la barre de recherche."""
    color = theme.TEXT_MUTED
    canvas.create_oval(7, 5, 19, 17, outline=color, width=2)
    canvas.create_line(18, 16, 24, 22, fill=color, width=2, capstyle=tk.ROUND)


class TrashIcon(tk.Canvas):
    """Corbeille dessinée au Canvas en terracotta, sans emoji."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(
            master,
            width=36,
            height=34,
            bg=theme.SURFACE,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        color = theme.TERRACOTTA
        self.create_line(9, 10, 27, 10, fill=color, width=2, capstyle=tk.ROUND)
        self.create_line(14, 6, 22, 6, fill=color, width=2, capstyle=tk.ROUND)
        self.create_line(12, 12, 13, 26, fill=color, width=2)
        self.create_line(24, 12, 23, 26, fill=color, width=2)
        self.create_line(13, 26, 23, 26, fill=color, width=2)
        self.create_line(16, 14, 16, 23, fill=color, width=1)
        self.create_line(20, 14, 20, 23, fill=color, width=1)


class PageFooter(ctk.CTkFrame):
    """Pied de page commun : navigation, sauvegarde et statistiques réelles."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        store: LibraryStore,
        primary_text: str,
        primary_command: Command,
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
        )
        self.store = store
        self.grid_columnconfigure(2, weight=1)

        options = {
            "font": theme.font(14),
            "height": 36,
            "corner_radius": theme.CORNER_RADIUS,
            "border_width": 0,
            "fg_color": theme.BACKGROUND,
            "hover_color": theme.HOVER,
            "text_color": theme.TEXT,
        }
        ctk.CTkButton(
            self,
            text=primary_text,
            width=150,
            command=primary_command,
            **options,
        ).grid(row=0, column=0, padx=(12, 6), pady=12)
        self.backup_button = ctk.CTkButton(
            self,
            text="Créer sauvegarde",
            width=150,
            command=self._create_backup,
            **options,
        )
        self.backup_button.grid(row=0, column=1, padx=6, pady=12)

        self.message_label = ctk.CTkLabel(
            self,
            text="",
            font=theme.font(11, slant="italic"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=800,
        )
        self.message_label.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=(12, 18),
            pady=(0, 10),
        )
        # Le pied de page garde sa hauteur tant qu'aucun message n'est affiché.
        self.message_label.grid_remove()

        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=0, column=2, sticky="e", padx=(12, 18))
        self._stat_labels: list[ctk.CTkLabel] = []
        for column in range(4):
            label = ctk.CTkLabel(
                stats_frame,
                text="",
                font=theme.font(12),
                text_color=theme.TEXT_MUTED,
            )
            label.grid(row=0, column=column, padx=5)
            self._stat_labels.append(label)

        self.update_stats()

    def update_stats(self) -> None:
        stats = self.store.stats
        labels = (
            _plural(stats["books"], "livre", "livres"),
            _plural(stats["available"], "livre disponible", "livres disponibles"),
            _plural(stats["borrowed"], "livre emprunté", "livres empruntés"),
            _plural(stats["users"], "utilisateur", "utilisateurs"),
        )
        for label, text in zip(self._stat_labels, labels):
            label.configure(text=text)

    def _create_backup(self) -> None:
        """Copie les fichiers de données dans leurs `.backup` via le moteur C++."""
        try:
            created = self.store.create_backup()
        except OSError as exc:
            self.show_message(str(exc), kind="error")
            return

        if not created:
            self.show_message("Aucun fichier à sauvegarder.", kind="muted")
            return

        self.show_message("Sauvegarde créée.")

    def show_message(self, text: str, kind: str = "success") -> None:
        colors = {
            "success": theme.SAGE,
            "error": theme.TERRACOTTA,
            "muted": theme.TEXT_MUTED,
        }
        self.message_label.configure(text=text, text_color=colors[kind])
        self.message_label.grid()


class BookCard(ctk.CTkFrame):
    """Carte d'un livre : titre, auteur, ISBN et actions."""

    HEIGHT = 158

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        book: Book,
        on_borrow: Callable[[Book], None],
        on_return: Callable[[Book], None],
        on_delete: Callable[[Book], None],
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            height=self.HEIGHT,
        )
        self.book = book
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=book.title,
            font=theme.font(17, "bold"),
            text_color=theme.TEXT,
            anchor="w",
            justify="left",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))

        self.author_label = ctk.CTkLabel(
            self,
            text=book.author,
            font=theme.font(13),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            justify="left",
        )
        self.author_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 0))

        ctk.CTkLabel(
            self,
            text=f"ISBN {book.isbn}",
            font=theme.font(11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 0))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="ew", padx=14, pady=(6, 12))
        actions.grid_columnconfigure(0, weight=1)

        # Emprunt et retour sont branchés ; la suppression viendra ensuite.
        self.action_button = ctk.CTkButton(
            actions,
            text="Emprunter" if book.available else "Retourner",
            command=(lambda: on_borrow(book))
            if book.available
            else (lambda: on_return(book)),
            width=118,
            height=32,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.BACKGROUND,
            hover_color=theme.HOVER,
            text_color=theme.TEXT,
            font=theme.font(13),
        )
        self.action_button.grid(row=0, column=0, sticky="w")
        self.trash_icon = TrashIcon(actions)
        self.trash_icon.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.trash_icon.bind("<Button-1>", lambda _event: on_delete(book))

        self.bind("<Configure>", self._wrap_texts)

    def _wrap_texts(self, event: Event) -> None:
        """Replie le titre et l'auteur plutôt que de les laisser déborder."""
        wrap = max(event.width - 28, 40)
        if wrap != getattr(self, "_wrap", None):
            self._wrap = wrap
            self.title_label.configure(wraplength=wrap)
            self.author_label.configure(wraplength=wrap)


class BooksView(ctk.CTkFrame):
    """Page Livres, écran principal : en-tête, recherche, filtre et cartes."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        store: LibraryStore,
        on_show_users: Command,
    ) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, corner_radius=0)
        self.store = store
        self.on_show_users = on_show_users
        self._active_query = ""
        self._active_filter = "all"
        self._borrow_panel: BorrowPanel | None = None
        self._add_book_panel: AddBookPanel | None = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_search()
        self._build_filter()
        self._build_cards()
        self._build_footer()

    # ------------------------------------------------------------- interface
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(theme.PAGE_PADDING, 4),
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Livres",
            font=theme.font(20, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

    def _build_search(self) -> None:
        frame = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            height=44,
        )
        frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(0, 18),
        )
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)

        # Le texte n'est pris en compte qu'au clic sur la loupe.
        self.search_entry = ctk.CTkEntry(
            frame,
            height=36,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.SURFACE,
            text_color=theme.TEXT,
            placeholder_text="Rechercher",
            placeholder_text_color=theme.TEXT_MUTED,
            font=theme.font(14),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(14, 6), pady=4)
        self.search_entry.bind("<Return>", self._on_search_return)

        self.search_icon = tk.Canvas(
            frame,
            width=32,
            height=32,
            bg=theme.SURFACE,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.search_icon.grid(row=0, column=1, padx=(0, 10))
        _draw_magnifier(self.search_icon)
        self.search_icon.bind("<Button-1>", self._apply_search)

    def _build_filter(self) -> None:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(0, 8),
        )
        row.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            row,
            text="Filtrer par",
            font=theme.font(13),
            text_color=theme.TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        # Filtre appliqué immédiatement ; seuls les livres disponibles sont
        # proposés comme restriction.
        self.filter_menu = ctk.CTkOptionMenu(
            row,
            values=["Tous", "Disponibles"],
            command=self._on_filter_change,
            width=170,
            height=34,
            corner_radius=theme.CORNER_RADIUS,
            fg_color=theme.SURFACE,
            button_color=theme.HOVER,
            button_hover_color=theme.SAGE_SOFT,
            text_color=theme.TEXT,
            dropdown_fg_color=theme.SURFACE,
            dropdown_hover_color=theme.HOVER,
            dropdown_text_color=theme.TEXT,
            font=theme.font(13),
            dropdown_font=theme.font(13),
        )
        self.filter_menu.set("Tous")
        self.filter_menu.grid(row=0, column=1, sticky="w")

        self.add_book_button = ctk.CTkButton(
            row,
            text="Livre +",
            font=theme.font(15),
            width=130,
            height=40,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.SAGE,
            hover_color=theme.SAGE_HOVER,
            text_color=theme.BACKGROUND,
            command=self._open_add_book,
        )
        self.add_book_button.grid(row=0, column=3, sticky="e")

    def _build_cards(self) -> None:
        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BACKGROUND,
            corner_radius=0,
            scrollbar_fg_color=theme.BACKGROUND,
            scrollbar_button_color=theme.SAGE_SOFT,
            scrollbar_button_hover_color=theme.SAGE,
        )
        self.cards_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=theme.PAGE_PADDING - theme.CARD_GAP,
            pady=2,
        )
        for column in range(BOOK_COLUMNS):
            self.cards_frame.grid_columnconfigure(column, weight=1, uniform="books")

        self._populate_cards()

    def _on_filter_change(self, value: str) -> None:
        """Applique le filtre choisi dans le menu, sans toucher à la recherche."""
        self._active_filter = {"Tous": "all", "Disponibles": "available"}[value]
        self._refresh_cards()

    def _refresh_cards(self) -> None:
        self._populate_cards(
            self.store.filter_books(self._active_query, self._active_filter)
        )

    def _open_add_book(self) -> None:
        """Ouvre le panneau d'ajout de livre, une seule instance à la fois."""
        panel = self._add_book_panel
        if panel is not None and panel.is_open:
            panel.lift()
            panel.focus_force()
            return
        self._add_book_panel = AddBookPanel(
            self.winfo_toplevel(),
            self.store,
            self._on_book_added,
        )
        self._add_book_panel.show()

    def _on_book_added(self, _book: Book) -> None:
        """Rafraîchit la grille et les statistiques après un ajout réussi."""
        self._refresh_cards()
        self.footer.update_stats()

    def _open_borrow(self, book: Book) -> None:
        """Ouvre le panneau de choix de l'emprunteur pour ce livre."""
        panel = self._borrow_panel
        if panel is not None and panel.is_open:
            panel.lift()
            panel.focus_force()
            return
        self._borrow_panel = BorrowPanel(
            self.winfo_toplevel(),
            self.store,
            book,
            self._on_book_borrowed,
        )
        self._borrow_panel.show()

    def _on_book_borrowed(self, book: Book, borrower: str) -> None:
        """Rafraîchit la grille et le pied de page après un emprunt réussi."""
        self._refresh_cards()
        self.footer.update_stats()
        self.footer.show_message(f"« {book.title} » emprunté par {borrower}.")

    def _return_book(self, book: Book) -> None:
        """Rend le livre disponible, sans changer l'emprunteur en cas d'échec."""
        borrower_id = book.borrower_id
        borrower = self.store.find_user(borrower_id)
        borrower_label = (
            f"{borrower.name} ({borrower.user_id})" if borrower else borrower_id
        )

        try:
            self.store.return_book(book.isbn)
        except StoreError as exc:
            # Vue obsolète : on réaligne la grille sur le moteur.
            self._refresh_cards()
            self.footer.update_stats()
            self.footer.show_message(str(exc), kind="error")
            return

        try:
            self.store.save()
        except OSError as exc:
            # Le moteur a déjà modifié la mémoire : on remet l'emprunt en place
            # pour rester cohérent avec les fichiers, inchangés.
            try:
                self.store.checkout(book.isbn, borrower_id)
            except StoreError:
                pass
            # Réaligne la grille sur l'état réel après la tentative d'annulation.
            self._refresh_cards()
            self.footer.update_stats()
            self.footer.show_message(f"Erreur de sauvegarde : {exc}", kind="error")
            return

        self._refresh_cards()
        self.footer.update_stats()
        self.footer.show_message(f"« {book.title} » retourné par {borrower_label}.")

    def _delete_book(self, book: Book) -> None:
        """Supprime le livre, emprunt compris, sans confirmation."""
        try:
            self.store.remove_book(book.isbn)
        except StoreError as exc:
            # Vue obsolète : on réaligne la grille sur le moteur.
            self._refresh_cards()
            self.footer.update_stats()
            self.footer.show_message(str(exc), kind="error")
            return

        try:
            self.store.save()
        except OSError as exc:
            # Le disque est intact : on y relit l'état exact (livre, emprunt
            # et liste de l'utilisateur) plutôt que de le reconstruire.
            self.store.load()
            self._refresh_cards()
            self.footer.update_stats()
            self.footer.show_message(f"Erreur de sauvegarde : {exc}", kind="error")
            return

        self._refresh_cards()
        self.footer.update_stats()
        self.footer.show_message(f"« {book.title} » supprimé.")

    def _on_search_return(self, _event: Event | None = None) -> str | None:
        """Entrée ne réagit que sur un champ vide : réaffiche toute la bibliothèque."""
        if self.search_entry.get().strip():
            # Avec du texte, seule la loupe applique la recherche.
            return None

        self._active_query = ""
        self._refresh_cards()
        return "break"

    def _apply_search(self, _event: Event | None = None) -> None:
        """Filtre les cartes sur le texte courant (titre ou auteur)."""
        self._active_query = self.search_entry.get().strip()
        self._refresh_cards()

    def _populate_cards(self, books: list[Book] | None = None) -> None:
        visible = self.store.books if books is None else books
        for child in self.cards_frame.winfo_children():
            child.destroy()

        if not visible:
            if self._active_query:
                text = f"Aucun livre ne correspond à « {self._active_query} »."
            elif self._active_filter != "all":
                text = "Aucun livre dans ce filtre."
            else:
                text = "Aucun livre."
            ctk.CTkLabel(
                self.cards_frame,
                text=text,
                font=theme.font(14),
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=0, columnspan=BOOK_COLUMNS, pady=32)
            return

        for index, book in enumerate(visible):
            BookCard(
                self.cards_frame,
                book,
                self._open_borrow,
                self._return_book,
                self._delete_book,
            ).grid(
                row=index // BOOK_COLUMNS,
                column=index % BOOK_COLUMNS,
                sticky="nsew",
                padx=theme.CARD_GAP,
                pady=theme.CARD_GAP,
            )

    def _build_footer(self) -> None:
        self.footer = PageFooter(self, self.store, "Voir utilisateurs", self.on_show_users)
        self.footer.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(4, theme.PAGE_PADDING),
        )


class UserCard(ctk.CTkFrame):
    """Carte d'un utilisateur : nom, identifiant et nombre d'emprunts."""

    def __init__(self, master: ctk.CTkBaseClass, user: User) -> None:
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            height=136,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.name_label = ctk.CTkLabel(
            self,
            text=user.name,
            font=theme.font(17, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        )
        self.name_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(13, 0))
        self.bind("<Configure>", self._wrap_name)

        ctk.CTkLabel(
            self,
            text=user.user_id,
            font=theme.font(12),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 0))

        ctk.CTkLabel(
            self,
            text=_borrowed_text(len(user.borrowed)),
            font=theme.font(12),
            text_color=theme.TEXT_MUTED,
            anchor="center",
        ).grid(row=2, column=0, sticky="sew", padx=14, pady=(8, 13))

    def _wrap_name(self, event: Event) -> None:
        """Replie un nom trop long plutôt que de le laisser déborder."""
        wrap = max(event.width - 28, 40)
        if wrap != getattr(self, "_name_wrap", None):
            self._name_wrap = wrap
            self.name_label.configure(wraplength=wrap)


class UsersView(ctk.CTkFrame):
    """Page Utilisateurs : en-tête, grille de cartes et pied de page."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        store: LibraryStore,
        on_show_books: Command,
    ) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, corner_radius=0)
        self.store = store
        self.on_show_books = on_show_books
        self._add_user_panel: AddUserPanel | None = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_cards()
        self._build_footer()

    # ------------------------------------------------------------- interface
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(theme.PAGE_PADDING, 8),
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Utilisateurs",
            font=theme.font(20, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="Utilisateur +",
            font=theme.font(15),
            width=150,
            height=40,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.SAGE,
            hover_color=theme.SAGE_HOVER,
            text_color=theme.BACKGROUND,
            command=self._open_add_user,
        ).grid(row=0, column=1, sticky="e")

    def _open_add_user(self) -> None:
        panel = self._add_user_panel
        if panel is not None and panel.is_open:
            panel.lift()
            panel.focus_force()
            return
        self._add_user_panel = AddUserPanel(
            self.winfo_toplevel(),
            self.store,
            self._on_user_saved,
        )
        self._add_user_panel.show()

    def _on_user_saved(self, _user: User) -> None:
        self._populate_cards()
        self.footer.update_stats()

    def _build_cards(self) -> None:
        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BACKGROUND,
            corner_radius=0,
            scrollbar_fg_color=theme.BACKGROUND,
            scrollbar_button_color=theme.SAGE_SOFT,
            scrollbar_button_hover_color=theme.SAGE,
        )
        self.cards_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=theme.PAGE_PADDING - theme.CARD_GAP,
            pady=2,
        )
        for column in range(USER_COLUMNS):
            self.cards_frame.grid_columnconfigure(column, weight=1, uniform="users")

        self._populate_cards()

    def _populate_cards(self) -> None:
        for child in self.cards_frame.winfo_children():
            child.destroy()

        if not self.store.users:
            ctk.CTkLabel(
                self.cards_frame,
                text="Aucun utilisateur.",
                font=theme.font(14),
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=0, columnspan=USER_COLUMNS, pady=32)
            return

        for index, user in enumerate(self.store.users):
            UserCard(self.cards_frame, user).grid(
                row=index // USER_COLUMNS,
                column=index % USER_COLUMNS,
                sticky="nsew",
                padx=theme.CARD_GAP,
                pady=theme.CARD_GAP,
            )

    def _build_footer(self) -> None:
        self.footer = PageFooter(self, self.store, "Voir livres", self.on_show_books)
        self.footer.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(4, theme.PAGE_PADDING),
        )
