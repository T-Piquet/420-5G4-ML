"""Livre de la bibliothèque."""

from dataclasses import dataclass


@dataclass
class Book:
    """Livre avec son état de disponibilité."""

    title: str
    author: str
    isbn: str
    available: bool = True
    borrower_id: str = ""
