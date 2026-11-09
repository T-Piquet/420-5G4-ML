"""Conversion des entités du modèle en cellules de tableau."""
from gui.models.entities import Book
from gui.views.table import Status, TwoLines


def book_cell(book: Book) -> TwoLines:
    return TwoLines(book.title, book.author)


def book_status(book: Book) -> Status:
    return Status("Disponible", True) if book.available else Status("Emprunté", False)


def plural(count: int, singular: str, plural_form: str | None = None) -> str:
    word = singular if count <= 1 else (plural_form or f"{singular}s")
    return f"{count} {word}"
