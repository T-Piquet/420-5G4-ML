"""Contrôleur principal : relie le modèle, la persistance et la vue."""

from __future__ import annotations

from app.models.book import Book
from app.models.library import Library, LibraryError
from app.repositories.library_repository import LibraryRepository
from app.views.main_window import MainWindow
from app.views.view_models import BookRow, UserRow


def plural(count: int, singular: str, plural_form: str) -> str:
    """Accorde un compteur en français (0 et 1 restent au singulier)."""
    return f"{count} {singular if count <= 1 else plural_form}"


class MainController:
    """Traduit les actions de la vue en opérations sur le modèle."""

    def __init__(
        self,
        model: Library,
        view: MainWindow,
        repository: LibraryRepository,
    ) -> None:
        self.model = model
        self.view = view
        self.repository = repository

        self._query = ""
        self._selected_isbn: str | None = None

        self.view.set_search_callback(self.on_search)
        self.view.set_select_callback(self.on_select)
        self.view.set_navigation_callback(self.on_navigate)
        self.view.set_add_callback(self.on_add_requested)
        self.view.set_borrow_callback(self.on_borrow_requested)
        self.view.set_delete_callback(self.on_delete_requested)

        self.refresh()

    # Actions déclenchées par la vue

    def on_search(self, query: str) -> None:
        """Filtre la liste à partir du champ de recherche."""
        if query == self._query:
            return
        self._query = query
        self.refresh()

    def on_select(self, isbn: str) -> None:
        """Mémorise le livre sélectionné et adapte les actions."""
        if isbn == self._selected_isbn:
            return
        self._selected_isbn = isbn
        self.view.set_selected(isbn)
        self._update_selection()
        self.view.set_status("")

    def on_navigate(self, section: str) -> None:
        """Réapplique les informations de la section Livres."""
        if section == "Livres":
            self._update_selection()

    def on_add_requested(self) -> None:
        self.view.open_add_dialog(self._submit_add)

    def on_borrow_requested(self) -> None:
        book = self._selected_book()
        if book is None:
            return

        if book.available:
            if not self.model.users:
                self.view.set_status(
                    "Aucun utilisateur enregistré pour un emprunt.", "error"
                )
                return
            users = [
                UserRow(user_id=user.user_id, name=user.name)
                for user in self.model.users
            ]
            self.view.open_borrow_dialog(book.title, users, self._submit_borrow)
            return

        self._return_selected(book)

    def on_delete_requested(self) -> None:
        book = self._selected_book()
        if book is None:
            return
        if not self.view.confirm_delete(book.title):
            return

        try:
            self.model.remove_book(book.isbn)
        except LibraryError as error:
            self.view.set_status(str(error), "error")
            return

        self._selected_isbn = None
        self.refresh()
        if self._save():
            self.view.set_status("Livre supprimé.", "success")

    # Soumissions des dialogues

    def _submit_add(self, title: str, author: str, isbn: str) -> str | None:
        try:
            book = self.model.add_book(title, author, isbn)
        except LibraryError as error:
            return str(error)

        self._selected_isbn = book.isbn
        self._query = ""
        self.view.clear_search()
        self.refresh()
        if self._save():
            self.view.set_status("Livre ajouté.", "success")
        return None

    def _submit_borrow(self, user_id: str) -> str | None:
        book = self._selected_book()
        if book is None:
            return "Aucun livre sélectionné."

        try:
            self.model.borrow(book.isbn, user_id)
        except LibraryError as error:
            return str(error)

        self.refresh()
        if self._save():
            self.view.set_status("Livre emprunté.", "success")
        return None

    def _return_selected(self, book: Book) -> None:
        try:
            self.model.return_book(book.isbn)
        except LibraryError as error:
            self.view.set_status(str(error), "error")
            return

        self.refresh()
        if self._save():
            self.view.set_status("Livre retourné.", "success")

    # Rafraîchissement

    def refresh(self) -> None:
        """Reconstruit les lignes affichées et les compteurs."""
        if self._selected_isbn is not None and self.model.find_book(
            self._selected_isbn
        ) is None:
            self._selected_isbn = None

        books = self.model.filtered_books(self._query)
        visible_isbns = {book.isbn for book in books}
        if (
            self._selected_isbn is not None
            and self._selected_isbn not in visible_isbns
        ):
            self._selected_isbn = None

        self.view.set_books([self._to_row(book) for book in books])
        self.view.set_selected(self._selected_isbn)

        stats = self.model.statistics()
        self.view.set_section_subtitle(
            f"{plural(stats.total, 'livre', 'livres')} · "
            f"{plural(stats.borrowed, 'emprunté', 'empruntés')}"
        )
        self._update_selection()

    def _update_selection(self) -> None:
        book = self._selected_book()
        if book is None:
            stats = self.model.statistics()
            self.view.set_actions(
                can_delete=False,
                can_borrow=False,
                borrow_label="Emprunter",
            )
            self.view.set_footer_info(
                f"{plural(stats.total, 'livre', 'livres')} · "
                f"{plural(stats.available, 'disponible', 'disponibles')} · "
                f"{plural(stats.borrowed, 'emprunté', 'empruntés')}"
            )
            return

        self.view.set_actions(
            can_delete=True,
            can_borrow=(not book.available) or bool(self.model.users),
            borrow_label="Emprunter" if book.available else "Retourner",
        )
        self.view.set_footer_info(self._selection_text(book))

    def _selection_text(self, book: Book) -> str:
        if book.available:
            return f"Sélection : {book.title} — Disponible"

        borrower = self.model.borrower_name(book)
        if borrower:
            return f"Sélection : {book.title} — Emprunté par {borrower}"
        return f"Sélection : {book.title} — Emprunté"

    @staticmethod
    def _to_row(book: Book) -> BookRow:
        return BookRow(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            status_label="Disponible" if book.available else "Emprunté",
            available=book.available,
        )

    def _selected_book(self) -> Book | None:
        if self._selected_isbn is None:
            return None
        return self.model.find_book(self._selected_isbn)

    def _save(self) -> bool:
        try:
            self.repository.save(self.model)
        except OSError:
            self.view.set_status(
                "Impossible d'enregistrer les données de la bibliothèque.",
                "error",
            )
            return False
        return True
