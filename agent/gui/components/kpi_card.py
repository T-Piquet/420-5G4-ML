"""Carte de statistique (KPI) reutilisable."""

from __future__ import annotations

import customtkinter as ctk


class KPICard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str | int = "0",
        accent: str = "#3b82f6",
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            corner_radius=14,
            fg_color=("gray93", "gray17"),
            **kwargs,
        )
        self.grid_columnconfigure(1, weight=1)

        self.accent_bar = ctk.CTkFrame(
            self,
            width=6,
            corner_radius=3,
            fg_color=accent,
        )
        self.accent_bar.grid(
            row=0, column=0, rowspan=2, sticky="ns", padx=(16, 0), pady=16
        )

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray65"),
        )
        self.title_label.grid(
            row=0, column=1, sticky="ew", padx=(12, 16), pady=(16, 0)
        )

        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            anchor="w",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=accent,
        )
        self.value_label.grid(
            row=1, column=1, sticky="ew", padx=(12, 16), pady=(0, 16)
        )

    def set_value(self, value: str | int) -> None:
        self.value_label.configure(text=str(value))
