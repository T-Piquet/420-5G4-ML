"""Recherche de livres partagée par l'accueil et le catalogue."""
from gui.models.entities import Book
from gui.models.library_model import LibraryModel


def search_books(model: LibraryModel, criterion: str, query: str) -> list[Book]:
    if criterion == "Titre":
        return model.search_by_title(query)
    if criterion == "Auteur":
        return model.search_by_author(query)
    book = model.find_book(query)
    return [book] if book else []


def no_result_message(criterion: str, query: str) -> str:
    if criterion == "ISBN":
        return f"Aucun livre n'a l'ISBN {query}.\nSaisissez le numéro complet, sans espaces."
    field = "titre" if criterion == "Titre" else "auteur"
    return f"Aucun {field} ne contient « {query} ».\nVérifiez l'orthographe et les accents."
