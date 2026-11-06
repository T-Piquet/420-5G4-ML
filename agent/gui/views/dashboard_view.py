"""Tableau de bord avec les indicateurs principaux et la sauvegarde."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from gui.components.dialogs import show_error
from gui.components.kpi_card import KPICard
from gui.service import LibraryError, LibraryService


class DashboardView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        service: LibraryService,
        on_mutation: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.service = service
        self.on_mutation = on_mutation
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        intro = ctk.CTkLabel(
            self,
            text="Vue d'ensemble de votre bibliothèque personnelle.",
            anchor="w",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray65"),
        )
        intro.grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16)
        )

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew"
        )
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)

        self.cards: dict[str, KPICard] = {}
        definitions = [
            ("total", "Total des livres", "#3b82f6"),
            ("available", "Livres disponibles", "#22c55e"),
            ("checked_out", "Emprunts en cours", "#f59e0b"),
            ("users", "Adhérents", "#a855f7"),
        ]
        for index, (key, title, accent) in enumerate(definitions):
            card = KPICard(cards_frame, title=title, value="0", accent=accent)
            card.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=(0, 8) if index % 2 == 0 else (8, 0),
                pady=(0, 16),
            )
            self.cards[key] = card

        info = ctk.CTkFrame(
            self,
            fg_color=("gray93", "gray17"),
            corner_radius=14,
        )
        info.grid(
            row=2, column=0, columnspan=2, sticky="nsew", pady=(8, 0)
        )
        info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info,
            text="À propos de cette interface",
            anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))

        ctk.CTkLabel(
            info,
            text=(
                "Les ajouts, suppressions, emprunts et retours sont "
                "enregistrés automatiquement dans le répertoire de "
                "données. Utilisez le bouton ci-dessous pour conserver "
                "une copie de sécurité des fichiers actuels."
            ),
            anchor="w",
            justify="left",
            wraplength=820,
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray65"),
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 14))

        self.backup_button = ctk.CTkButton(
            info,
            text="Créer une sauvegarde (Backup)",
            width=250,
            height=38,
            command=self._create_backup,
        )
        self.backup_button.grid(
            row=2, column=0, sticky="w", padx=20, pady=(0, 10)
        )

        ctk.CTkLabel(
            info,
            text=(
                "La sauvegarde copie books.txt et users.txt en "
                "books.txt.backup et users.txt.backup."
            ),
            anchor="w",
            justify="left",
            wraplength=820,
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray55"),
        ).grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 18))

    def refresh(self) -> None:
        stats = self.service.get_stats()
        self.cards["total"].set_value(stats.total_books)
        self.cards["available"].set_value(stats.available_books)
        self.cards["checked_out"].set_value(stats.checked_out_books)
        self.cards["users"].set_value(stats.users)

    def _create_backup(self) -> None:
        try:
            names = self.service.create_backup()
        except LibraryError as exc:
            show_error(self, str(exc), title="Sauvegarde impossible")
            return

        self.on_mutation(
            "Sauvegarde créée : " + ", ".join(names) + "."
        )
