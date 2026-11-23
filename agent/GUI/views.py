"""Vues de l'application (une seule pour l'instant : les utilisateurs)."""

from __future__ import annotations

from tkinter import Event

import customtkinter as ctk

import theme
from data_store import LibraryStore, User
from panels import AddUserPanel

COLUMNS = 4


def _plural(count: int, singular: str, plural: str) -> str:
    """Accorde un nom avec son nombre (0 et 1 restent au singulier)."""
    return f"{count} {singular if count <= 1 else plural}"


def _borrowed_text(count: int) -> str:
    if count == 0:
        return "Aucun livre emprunté"
    return _plural(count, "livre emprunté", "livres empruntés")


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

    def __init__(self, master: ctk.CTkBaseClass, store: LibraryStore) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, corner_radius=0)
        self.store = store
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
        self._update_stats()

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
        for column in range(COLUMNS):
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
            ).grid(row=0, column=0, columnspan=COLUMNS, pady=32)
            return

        for index, user in enumerate(self.store.users):
            UserCard(self.cards_frame, user).grid(
                row=index // COLUMNS,
                column=index % COLUMNS,
                sticky="nsew",
                padx=theme.CARD_GAP,
                pady=theme.CARD_GAP,
            )

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
        )
        footer.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=theme.PAGE_PADDING,
            pady=(4, theme.PAGE_PADDING),
        )
        footer.grid_columnconfigure(2, weight=1)

        button_options = {
            "font": theme.font(14),
            "height": 36,
            "corner_radius": theme.CORNER_RADIUS,
            "border_width": 0,
            "fg_color": theme.BACKGROUND,
            "hover_color": theme.HOVER,
            "text_color": theme.TEXT,
        }
        # Boutons encore inactifs : ils seront branchés avec les autres vues.
        ctk.CTkButton(footer, text="Voir livres", width=120, **button_options).grid(
            row=0, column=0, padx=(12, 6), pady=12
        )
        ctk.CTkButton(footer, text="Créer sauvegarde", width=150, **button_options).grid(
            row=0, column=1, padx=6, pady=12
        )

        stats_frame = ctk.CTkFrame(footer, fg_color="transparent")
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

        self._update_stats()

    def _update_stats(self) -> None:
        stats = self.store.stats
        labels = (
            _plural(stats["books"], "livre", "livres"),
            _plural(stats["available"], "livre disponible", "livres disponibles"),
            _plural(stats["borrowed"], "livre emprunté", "livres empruntés"),
            _plural(stats["users"], "utilisateur", "utilisateurs"),
        )
        for label, text in zip(self._stat_labels, labels):
            label.configure(text=text)
