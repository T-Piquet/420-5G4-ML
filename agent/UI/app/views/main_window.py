"""Vue principale construite avec customtkinter.

La vue ne contient aucune logique métier : elle expose des méthodes de mise à
jour et transmet les actions de l'utilisateur au contrôleur via un callback.
"""

from collections.abc import Callable

import customtkinter as ctk

from app import config


class MainWindow(ctk.CTk):
    """Fenêtre principale de l'application."""

    def __init__(self) -> None:
        super().__init__()

        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(640, 420)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.message_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.message_label.grid(row=0, column=0, padx=24, pady=(32, 16), sticky="ew")

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(
            row=1, column=0, padx=24, pady=(0, 32), sticky="nsew"
        )
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.counter_label = ctk.CTkLabel(
            self.content_frame,
            text="0",
            font=ctk.CTkFont(size=48, weight="bold"),
        )
        self.counter_label.grid(row=0, column=0, pady=(48, 16))

        self.increment_button = ctk.CTkButton(
            self.content_frame,
            text="Incrémenter",
            width=180,
            command=self._on_increment_click,
        )
        self.increment_button.grid(row=1, column=0, pady=(0, 48))

        self._increment_callback: Callable[[], None] | None = None

    def set_message(self, message: str) -> None:
        """Affiche le message fourni par le modèle."""
        self.message_label.configure(text=message)

    def set_counter(self, value: int) -> None:
        """Affiche la valeur courante du compteur."""
        self.counter_label.configure(text=str(value))

    def set_increment_callback(self, callback: Callable[[], None]) -> None:
        """Enregistre l'action déclenchée par le bouton."""
        self._increment_callback = callback

    def _on_increment_click(self) -> None:
        if self._increment_callback is not None:
            self._increment_callback()
