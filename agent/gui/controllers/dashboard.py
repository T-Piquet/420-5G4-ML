"""Contrôleur de la page d'accueil."""
from collections.abc import Callable
from functools import partial

from gui.controllers.actions import ActionsController
from gui.controllers.book_search import no_result_message, search_books
from gui.controllers.presenters import book_cell, book_status
from gui.models.entities import Book
from gui.models.library_model import LibraryModel
from gui.views.pages.dashboard import DashboardPage
from gui.views.shelf import Spine
from gui.views.table import Action

_PREVIEW_SIZE = 5
_MAX_RESULTS = 4


class DashboardController:
    def __init__(self, model: LibraryModel, view: DashboardPage, actions: ActionsController,
                 navigate: Callable[[str], None]) -> None:
        self._model = model
        self._view = view
        self._actions = actions
        view.on_add_book = actions.add_book
        view.on_lend = actions.lend
        view.on_return = actions.return_book
        view.on_add_member = actions.add_member
        view.on_save = actions.save
        view.on_open_catalog = partial(navigate, "catalog")
        view.on_search = self._show_results

    def refresh(self) -> None:
        stats = self._model.stats()
        self._view.show_figures([
            (stats.total_books, "Livres au total"),
            (stats.available_books, "Disponibles"),
            (stats.loaned_books, "Empruntés"),
            (stats.members, "Utilisateurs"),
        ])
        books = self._model.books()
        self._view.show_shelf([Spine(book.title, book.available) for book in books])
        self._view.show_preview(
            [self._row(book) for book in books[:_PREVIEW_SIZE]],
            "Le catalogue est vide. Ajoutez un premier livre.",
        )
        self._show_results()

    def _show_results(self) -> None:
        bar = self._view.search_bar
        if not bar.query:
            self._view.hide_results()
            return
        books = search_books(self._model, bar.criterion, bar.query)
        self._view.show_results(
            [self._row(book) for book in books[:_MAX_RESULTS]],
            no_result_message(bar.criterion, bar.query),
        )

    def _row(self, book: Book) -> tuple:
        action = (
            Action("Emprunter", partial(self._actions.lend, book.isbn))
            if book.available
            else Action("Retourner", partial(self._actions.return_book, book.isbn))
        )
        return (book_cell(book), book.isbn, book_status(book), (action,))
