"""Contrôleur des emprunts en cours."""
from functools import partial

from gui.controllers.actions import ActionsController
from gui.controllers.presenters import book_cell, plural
from gui.models.entities import Book
from gui.models.library_model import LibraryModel
from gui.views.pages.loans import LoansPage
from gui.views.table import Action


class LoansController:
    def __init__(self, model: LibraryModel, view: LoansPage, actions: ActionsController) -> None:
        self._model = model
        self._view = view
        self._actions = actions
        view.on_lend = actions.lend
        view.on_return = actions.return_book

    def refresh(self) -> None:
        loans = self._model.loaned_books()
        self._view.show_loans(
            [self._row(book) for book in loans],
            "Aucun livre n'est emprunté pour le moment.",
            f"{plural(len(loans), 'livre emprunté', 'livres empruntés')} en ce moment.",
        )

    def _row(self, book: Book) -> tuple:
        member = self._model.find_member(book.borrower_id)
        return (
            book_cell(book),
            book.isbn,
            member.name if member else "Utilisateur inconnu",
            book.borrower_id,
            (Action("Retourner", partial(self._actions.return_book, book.isbn)),),
        )
