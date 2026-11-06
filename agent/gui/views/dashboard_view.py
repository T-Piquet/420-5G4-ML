"""Tableau de bord avec les indicateurs principaux."""

from __future__ import annotations

import customtkinter as ctk

from gui.components.kpi_card import KPICard
from gui.service import LibraryService


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, service: LibraryService) -> None:
        super().__init__(master, fg_color="transparent")
        self.service = service
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
                "Cette version présente les données de la bibliothèque en "
                "lecture seule. Les actions d'ajout, de suppression, "
                "d'emprunt et de retour seront disponibles au jalon 4."
            ),
            anchor="w",
            justify="left",
            wraplength=820,
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray65"),
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 18))

    def refresh(self) -> None:
        stats = self.service.get_stats()
        self.cards["total"].set_value(stats.total_books)
        self.cards["available"].set_value(stats.available_books)
        self.cards["checked_out"].set_value(stats.checked_out_books)
        self.cards["users"].set_value(stats.users)
