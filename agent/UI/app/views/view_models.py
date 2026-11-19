"""Structures de données transmises par le contrôleur à la vue.

La vue ne doit pas importer le modèle : elle reçoit uniquement ces lignes
prêtes à afficher.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BookRow:
    """Ligne du tableau des livres."""

    isbn: str
    title: str
    author: str
    status_label: str
    available: bool


@dataclass(frozen=True)
class UserRow:
    """Utilisateur proposé dans la fenêtre d'emprunt."""

    user_id: str
    name: str
