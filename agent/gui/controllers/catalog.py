"""Contrôleur du catalogue."""
from functools import partial

from gui.controllers.actions import ActionsController
from gui.controllers.book_search import no_result_message, search_books
from gui.controllers.presenters import book_cell, book_status, plural
from gui.models.entities import Book
from gui.models.library_model import LibraryModel
from gui.views.pages.catalog import FILTER_AVAILABLE, CatalogPage
from gui.views.table import Action


class CatalogController:
    def __init__(self, model: LibraryModel, view: CatalogPage, actions: ActionsController) -> None:
        self._model = model
        self._view = view
        self._actions = actions
        view.on_add_book = actions.add_book
        view.on_search = self.refresh

    def refresh(self) -> None:
        bar = self._view.search_bar
        query = bar.query
        self._view.set_filter_enabled(not query)
        if query:
            books = search_books(self._model, bar.criterion, query)
            empty_text = no_result_message(bar.criterion, query)
            count_text = (
                f"{plural(len(books), 'résultat')} sur {self._model.stats().total_books} livres. "
                "Effacez la recherche pour utiliser le filtre Afficher."
            )
        elif self._view.availability_filter == FILTER_AVAILABLE:
            books = self._model.available_books()
            empty_text = "Aucun livre disponible. Tous les livres sont empruntés."
            count_text = plural(len(books), "livre disponible", "livres disponibles")
        else:
            books = self._model.books()
            empty_text = "Le catalogue est vide. Ajoutez un premier livre."
            count_text = plural(len(books), "livre")
        self._view.show_books([self._row(book) for book in books], empty_text, count_text)

    def focus_search(self) -> None:
        self._view.search_bar.focus_entry()

    def _row(self, book: Book) -> tuple:
        primary = (
            Action("Emprunter", partial(self._actions.lend, book.isbn))
            if book.available
            else Action("Retourner", partial(self._actions.return_book, book.isbn))
        )
        delete = Action(
            "Supprimer",
            partial(self._actions.remove_book, book.isbn, book.title),
            enabled=book.available,
        )
        return (book_cell(book), book.isbn, book_status(book), self._borrower(book), (primary, delete))

    def _borrower(self, book: Book) -> str:
        if book.available:
            return "—"
        member = self._model.find_member(book.borrower_id)
        return member.name if member else book.borrower_id
