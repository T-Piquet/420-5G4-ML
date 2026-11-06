"""Barre d'etat affichant le statut et le repertoire de donnees."""

from __future__ import annotations

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    COLORS = {
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
    }

    def __init__(self, master, data_path: str, **kwargs) -> None:
        super().__init__(
            master,
            height=38,
            corner_radius=0,
            fg_color=("gray88", "gray14"),
            **kwargs,
        )
        self.grid_columnconfigure(1, weight=1)

        self.dot = ctk.CTkLabel(
            self,
            text="●",
            width=20,
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["info"],
        )
        self.dot.grid(row=0, column=0, padx=(16, 0), pady=8)

        self.status_label = ctk.CTkLabel(
            self,
            text="Prêt",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray75"),
        )
        self.status_label.grid(
            row=0, column=1, sticky="ew", padx=(6, 12), pady=8
        )

        self.path_label = ctk.CTkLabel(
            self,
            text=f"Données : {data_path}",
            anchor="e",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        )
        self.path_label.grid(
            row=0, column=2, sticky="e", padx=(12, 16), pady=8
        )

    def set_status(self, message: str, kind: str = "info") -> None:
        color = self.COLORS.get(kind, self.COLORS["info"])
        self.dot.configure(text_color=color)
        self.status_label.configure(text=message)

    def set_data_path(self, path: str) -> None:
        self.path_label.configure(text=f"Données : {path}")
