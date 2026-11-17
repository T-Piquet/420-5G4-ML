"""Loans and returns page connected to BibliothequeAPI."""

import customtkinter as ctk

from theme import COLORS, FONTS, RADIUS
from ui.pages.base import BasePage


class SettingsPage(BasePage):
    """Page for book checkouts, returns, and manual data saving."""

    def __init__(self, master, api) -> None:
        super().__init__(master, api)

        ctk.CTkLabel(
            self,
            text="Prêt & retours",
            font=FONTS["title"],
            text_color=COLORS["text_light"],
        ).grid(row=0, column=0, padx=24, pady=(24, 16), sticky="w")

        form = ctk.CTkFrame(self, fg_color=COLORS["bg_row"], corner_radius=RADIUS["row"])
        form.grid(row=1, column=0, padx=24, pady=8, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="ISBN :", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).grid(
            row=0, column=0, padx=16, pady=(16, 8), sticky="w"
        )
        self.isbn_entry = ctk.CTkEntry(form, placeholder_text="Ex: 978-0-13-110362-7")
        self.isbn_entry.grid(row=0, column=1, padx=16, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(form, text="ID Membre :", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).grid(
            row=1, column=0, padx=16, pady=8, sticky="w"
        )
        self.user_entry = ctk.CTkEntry(form, placeholder_text="Ex: U001 (requis pour emprunt)")
        self.user_entry.grid(row=1, column=1, padx=16, pady=8, sticky="ew")

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=2, column=0, columnspan=2, padx=16, pady=(8, 16), sticky="w")

        ctk.CTkButton(
            actions,
            text="Emprunter",
            corner_radius=RADIUS["button"],
            command=self._on_checkout,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            actions,
            text="Retourner",
            corner_radius=RADIUS["button"],
            command=self._on_return,
        ).grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            actions,
            text="Sauvegarder",
            corner_radius=RADIUS["button"],
            fg_color=COLORS["bg_white_btn"],
            hover_color=COLORS["bg_white_btn_hover"],
            text_color=COLORS["text_primary"],
            command=self._on_save,
        ).grid(row=0, column=2)

        self.feedback_label = ctk.CTkLabel(
            self, text="", font=FONTS["body"], text_color=COLORS["text_light"], anchor="w"
        )
        self.feedback_label.grid(row=2, column=0, padx=24, pady=12, sticky="ew")

    def _on_checkout(self) -> None:
        _, msg = self.api.checkout_book(self.isbn_entry.get(), self.user_entry.get())
        self.feedback_label.configure(text=msg)

    def _on_return(self) -> None:
        _, msg = self.api.return_book(self.isbn_entry.get())
        self.feedback_label.configure(text=msg)

    def _on_save(self) -> None:
        ok = self.api.save()
        msg = "Données sauvegardées." if ok else "Erreur lors de la sauvegarde."
        self.feedback_label.configure(text=msg)
