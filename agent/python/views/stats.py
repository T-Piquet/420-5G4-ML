"""Onglet Statistiques : cartes de synthèse et sauvegardes."""

from __future__ import annotations

import customtkinter as ctk

CARDS = (
    ("total_books", "Livres"),
    ("available_books", "Disponibles"),
    ("checked_out_books", "Empruntés"),
    ("total_users", "Utilisateurs"),
)


class StatsView(ctk.CTkFrame):
    def __init__(self, master, service, on_status) -> None:
        super().__init__(master, fg_color="transparent")

        self.service = service
        self.on_status = on_status
        self._value_labels: dict[str, ctk.CTkLabel] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_cards()
        self._build_actions()

        self.refresh()

    # Construction de l'interface

    def _build_cards(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        container.grid_rowconfigure(0, weight=1)

        for column in range(len(CARDS)):
            container.grid_columnconfigure(column, weight=1)

        for column, (key, label) in enumerate(CARDS):
            card = ctk.CTkFrame(container, corner_radius=10)
            card.grid(row=0, column=column, sticky="nsew", padx=6, pady=6)

            value = ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=38, weight="bold"),
                anchor="center",
            )
            value.pack(fill="both", expand=True, padx=12, pady=(18, 4))

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=13),
                anchor="center",
            ).pack(fill="x", padx=12, pady=(0, 18))

            self._value_labels[key] = value

    def _build_actions(self) -> None:
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="e", padx=14, pady=(0, 10))

        ctk.CTkButton(
            actions, text="Sauvegarder", width=140, command=self._on_save
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            actions,
            text="Créer une sauvegarde",
            width=190,
            command=self._on_backup,
        ).grid(row=0, column=1)

    # Donnees

    def refresh(self) -> None:
        stats = self.service.get_stats()
        for key, label in self._value_labels.items():
            label.configure(text=str(stats.get(key, 0)))

    # Actions

    def _on_save(self) -> None:
        if self.service.save():
            self.on_status("Données sauvegardées dans books.txt et users.txt.")
        else:
            self.on_status("Impossible de sauvegarder les données.")

    def _on_backup(self) -> None:
        try:
            self.service.create_backup()
        except ValueError as error:
            self.on_status(str(error))
            return
        self.on_status("Sauvegarde créée : books.txt.backup et users.txt.backup.")
