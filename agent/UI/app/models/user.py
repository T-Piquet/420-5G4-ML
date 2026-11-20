"""Utilisateur de la bibliothèque."""

from dataclasses import dataclass, field


@dataclass
class User:
    """Utilisateur et liste des ISBN qu'il a empruntés."""

    name: str
    user_id: str
    borrowed_isbns: list[str] = field(default_factory=list)
