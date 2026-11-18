"""Modèle applicatif, indépendant de Tkinter."""

from dataclasses import dataclass


@dataclass
class AppModel:
    """État minimal de l'application."""

    message: str = "Bienvenue dans l'atelier ML"
    counter: int = 0

    def increment(self) -> int:
        """Incrémente le compteur et renvoie sa nouvelle valeur."""
        self.counter += 1
        return self.counter
