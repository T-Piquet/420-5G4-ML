"""Statistics overview page with save action."""

from typing import Dict
import customtkinter as ctk

from theme import COLORS, FONTS, RADIUS
from ui.pages.base import BasePage


class StatsPage(BasePage):
    """Displays library overview statistics and a Save button."""

    def __init__(self, master, api) -> None:
        super().__init__(master, api)
        self.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self,
            text="Statistiques de la bibliothèque",
            font=FONTS["title"],
            text_color=COLORS["text_light"],
        ).grid(row=0, column=0, columnspan=2, padx=24, pady=(24, 16), sticky="w")

        self._value_labels: Dict[str, ctk.CTkLabel] = {}
        cards = [
            ("total_books", "Livres au total", 1, 0),
            ("available_books", "Livres disponibles", 1, 1),
            ("checked_out_books", "Livres empruntés", 2, 0),
            ("total_users", "Nombre total d'utilisateurs", 2, 1),
        ]

        for key, title, row, col in cards:
            card = ctk.CTkFrame(self, fg_color=COLORS["bg_row"], corner_radius=RADIUS["row"])
            card.grid(row=row, column=col, padx=18, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=title,
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
            ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")

            val_label = ctk.CTkLabel(
                card,
                text="0",
                font=("Segoe UI", 28, "bold"),
                text_color=COLORS["text_primary"],
            )
            val_label.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="w")
            self._value_labels[key] = val_label

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=2, padx=24, pady=(20, 8), sticky="w")

        ctk.CTkButton(
            actions,
            text="Sauvegarder",
            height=38,
            corner_radius=RADIUS["button"],
            fg_color=COLORS["bg_white_btn"],
            hover_color=COLORS["bg_white_btn_hover"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_bold"],
            command=self._on_save,
        ).grid(row=0, column=0, padx=(0, 12))

        ctk.CTkButton(
            actions,
            text="Créer backup (.backup)",
            height=38,
            corner_radius=RADIUS["button"],
            fg_color=COLORS["bg_button"],
            hover_color=COLORS["bg_button_hover"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
            command=self._on_backup,
        ).grid(row=0, column=1)

        self.feedback_label = ctk.CTkLabel(
            self, text="", font=FONTS["body"], text_color=COLORS["text_light"], anchor="w"
        )
        self.feedback_label.grid(row=4, column=0, columnspan=2, padx=24, pady=(6, 18), sticky="ew")

    def refresh(self) -> None:
        stats = self.api.get_stats()
        for key, label in self._value_labels.items():
            label.configure(text=str(stats.get(key, 0)))

    def _on_save(self) -> None:
        ok = self.api.save()
        msg = "Données sauvegardées avec succès." if ok else "Erreur lors de la sauvegarde."
        self.feedback_label.configure(text=msg)

    def _on_backup(self) -> None:
        _, msg = self.api.create_backup()
        self.feedback_label.configure(text=msg)
