"""Panneau des statistiques de la bibliothèque.

Les valeurs affichées proviennent du modèle, lui-même alimenté par les
compteurs du cœur C++. La vue ne fait que les présenter.
"""

from __future__ import annotations

import customtkinter as ctk

from app import config
from app.views.view_models import StatisticsData


class StatCard(ctk.CTkFrame):
    """Carte blanche affichant un compteur et son libellé."""

    def __init__(
        self,
        master,
        *,
        title: str,
        caption: str,
        accent: str,
        soft: str,
    ) -> None:
        super().__init__(
            master,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=title.upper(),
            height=24,
            corner_radius=6,
            fg_color=soft,
            text_color=accent,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 0), ipadx=8)

        self._value_label = ctk.CTkLabel(
            self,
            text="0",
            anchor="w",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=config.COLOR_TEXT,
        )
        self._value_label.grid(row=1, column=0, sticky="w", padx=18, pady=(4, 0))

        ctk.CTkLabel(
            self,
            text=caption,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 16))

        self._value = 0

    @property
    def value(self) -> int:
        return self._value

    def set_value(self, value: int) -> None:
        self._value = value
        self._value_label.configure(text=str(value))


class StatisticsPanel(ctk.CTkFrame):
    """Tableau de bord : quatre compteurs et le taux de disponibilité."""

    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1, uniform="stat")
        self.grid_columnconfigure(1, weight=1, uniform="stat")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        definitions = (
            (
                "total",
                "Livres au total",
                "Dans la bibliothèque",
                config.COLOR_ACCENT,
                config.COLOR_ACCENT_SOFT,
            ),
            (
                "available",
                "Disponibles",
                "Prêts possibles",
                config.COLOR_SUCCESS,
                config.COLOR_SUCCESS_SOFT,
            ),
            (
                "borrowed",
                "Empruntés",
                "En circulation",
                config.COLOR_WARNING,
                config.COLOR_WARNING_SOFT,
            ),
            (
                "users",
                "Utilisateurs",
                "Comptes enregistrés",
                config.COLOR_ACCENT,
                config.COLOR_ACCENT_SOFT,
            ),
        )

        self.cards: dict[str, StatCard] = {}
        for index, (key, title, caption, accent, soft) in enumerate(definitions):
            card = StatCard(
                self,
                title=title,
                caption=caption,
                accent=accent,
                soft=soft,
            )
            card.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=(0, 7) if index % 2 == 0 else (7, 0),
                pady=(0, 7) if index < 2 else (7, 0),
            )
            self.cards[key] = card

        availability = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=config.COLOR_BORDER,
        )
        availability.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(7, 0)
        )
        availability.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            availability,
            text="TAUX DE DISPONIBILITÉ",
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=config.COLOR_TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 0))

        self.rate_value = ctk.CTkLabel(
            availability,
            text="0 %",
            anchor="w",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=config.COLOR_SUCCESS,
        )
        self.rate_value.grid(row=1, column=0, sticky="w", padx=18, pady=(4, 0))

        self.rate_caption = ctk.CTkLabel(
            availability,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=config.COLOR_TEXT_MUTED,
        )
        self.rate_caption.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 10))

        self.progress = ctk.CTkProgressBar(
            availability,
            height=10,
            corner_radius=5,
            fg_color=config.COLOR_BORDER,
            progress_color=config.COLOR_SUCCESS,
        )
        self.progress.grid(
            row=3, column=0, sticky="ew", padx=18, pady=(0, 16)
        )
        self.progress.set(0)

    def set_data(self, data: StatisticsData) -> None:
        """Met à jour les compteurs et la jauge de disponibilité."""
        self.cards["total"].set_value(data.total)
        self.cards["available"].set_value(data.available)
        self.cards["borrowed"].set_value(data.borrowed)
        self.cards["users"].set_value(data.users)

        self.rate_value.configure(text=f"{data.availability_rate} %")
        self.progress.set(data.availability_rate / 100)

        if data.total == 0:
            caption = "Aucun livre dans la bibliothèque."
        else:
            caption = (
                f"{data.available} livres disponibles sur {data.total}"
            )
        self.rate_caption.configure(text=caption)
