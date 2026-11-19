"""Tests du contrôleur avec une vue et un dépôt factices."""

import pytest

pytest.importorskip(
    "app.bibliotheque_core", reason="Module natif non compilé"
)

from app.controllers.main_controller import MainController
from app.models.book import Book
from app.models.library import Library
from app.models.user import User


class FakeView:
    """Vue minimale qui enregistre les appels du contrôleur."""

    def __init__(self) -> None:
        self.books = []
        self.selected = None
        self.actions = None
        self.footer_info = None
        self.status = None
        self.subtitle = None
        self.search_cleared = False

        self.add_dialog = None
        self.borrow_dialog = None
        self.delete_requested = None
        self.delete_answer = True

        self.search_callback = None
        self.select_callback = None
        self.navigation_callback = None
        self.add_callback = None
        self.borrow_callback = None
        self.delete_callback = None

    def set_search_callback(self, callback) -> None:
        self.search_callback = callback

    def set_select_callback(self, callback) -> None:
        self.select_callback = callback

    def set_navigation_callback(self, callback) -> None:
        self.navigation_callback = callback

    def set_add_callback(self, callback) -> None:
        self.add_callback = callback

    def set_borrow_callback(self, callback) -> None:
        self.borrow_callback = callback

    def set_delete_callback(self, callback) -> None:
        self.delete_callback = callback

    def set_books(self, rows) -> None:
        self.books = rows

    def set_selected(self, isbn) -> None:
        self.selected = isbn

    def set_actions(
        self,
        *,
        can_delete: bool,
        can_borrow: bool,
        borrow_label: str,
    ) -> None:
        self.actions = (can_delete, can_borrow, borrow_label)

    def set_footer_info(self, text: str) -> None:
        self.footer_info = text

    def set_status(self, message: str, level: str = "info") -> None:
        self.status = (message, level)

    def set_section_subtitle(self, text: str) -> None:
        self.subtitle = text

    def clear_search(self) -> None:
        self.search_cleared = True

    def open_add_dialog(self, on_submit) -> None:
        self.add_dialog = on_submit

    def open_borrow_dialog(self, book_title, users, on_submit) -> None:
        self.borrow_dialog = (book_title, users, on_submit)

    def confirm_delete(self, title: str) -> bool:
        self.delete_requested = title
        return self.delete_answer


class FakeRepository:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.saved = 0

    def save(self, library: Library) -> None:
        if self.fail:
            raise OSError("disque plein")
        self.saved += 1


def make_model() -> Library:
    return Library(
        books=[
            Book("Le Petit Prince", "Antoine de Saint-Exupéry", "9782070612758"),
            Book("L'Étranger", "Albert Camus", "9782070360024"),
            Book(
                "Les Misérables",
                "Victor Hugo",
                "9782253096337",
                available=False,
                borrower_id="USR001",
            ),
        ],
        users=[
            User("Marie Dubois", "USR001", ["9782253096337"]),
            User("Jean Martin", "USR002"),
        ],
    )


def build(repository=None, model=None):
    model = model or make_model()
    view = FakeView()
    repository = repository or FakeRepository()
    controller = MainController(model, view, repository)
    return model, view, repository, controller


def test_initial_state() -> None:
    _, view, _, _ = build()

    assert [row.isbn for row in view.books] == [
        "9782070612758",
        "9782070360024",
        "9782253096337",
    ]
    assert view.selected is None
    assert view.actions == (False, False, "Emprunter")
    assert view.subtitle == "3 livres · 1 emprunté"
    assert view.footer_info == "3 livres · 2 disponibles · 1 emprunté"


def test_search_filters_rows() -> None:
    _, view, _, _ = build()

    view.search_callback("miserables")

    assert [row.isbn for row in view.books] == ["9782253096337"]


def test_filtering_clears_hidden_selection() -> None:
    _, view, _, _ = build()
    view.select_callback("9782070612758")

    view.search_callback("miserables")

    assert view.selected is None
    assert view.actions == (False, False, "Emprunter")


def test_select_updates_actions_and_footer() -> None:
    _, view, _, _ = build()

    view.select_callback("9782253096337")

    assert view.selected == "9782253096337"
    assert view.actions == (True, True, "Retourner")
    assert "Marie Dubois" in view.footer_info

    view.select_callback("9782070612758")

    assert view.actions == (True, True, "Emprunter")
    assert "Disponible" in view.footer_info


def test_add_book_submits_and_saves() -> None:
    model, view, repository, _ = build()

    view.add_callback()
    assert view.add_dialog is not None
    assert view.add_dialog("Germinal", "Émile Zola", "9782253004226") is None

    assert model.find_book("9782253004226") is not None
    assert repository.saved == 1
    assert view.status == ("Livre ajouté.", "success")
    assert view.search_cleared is True
    assert len(view.books) == 4
    assert view.selected == "9782253004226"


def test_add_duplicate_returns_error() -> None:
    model, view, repository, _ = build()

    view.add_callback()
    error = view.add_dialog("Autre", "Auteur", "9782070612758")

    assert error is not None
    assert "existe déjà" in error
    assert len(model.books) == 3
    assert repository.saved == 0


def test_add_with_save_failure_shows_error() -> None:
    _, view, _, _ = build(FakeRepository(fail=True))

    view.add_callback()
    assert view.add_dialog("Germinal", "Émile Zola", "9782253004226") is None

    assert view.status == (
        "Impossible d'enregistrer les données de la bibliothèque.",
        "error",
    )


def test_delete_selected_book() -> None:
    model, view, repository, _ = build()
    view.select_callback("9782070612758")

    view.delete_callback()

    assert view.delete_requested == "Le Petit Prince"
    assert model.find_book("9782070612758") is None
    assert repository.saved == 1
    assert view.selected is None
    assert view.actions == (False, False, "Emprunter")
    assert view.status == ("Livre supprimé.", "success")


def test_delete_cancelled_keeps_book() -> None:
    model, view, repository, _ = build()
    view.select_callback("9782070612758")
    view.delete_answer = False

    view.delete_callback()

    assert model.find_book("9782070612758") is not None
    assert repository.saved == 0
    assert view.status[0] == ""


def test_borrow_selected_book() -> None:
    model, view, repository, _ = build()
    view.select_callback("9782070612758")

    view.borrow_callback()

    assert view.borrow_dialog is not None
    book_title, users, submit = view.borrow_dialog
    assert book_title == "Le Petit Prince"
    assert [user.user_id for user in users] == ["USR001", "USR002"]
    assert submit("USR002") is None

    book = model.find_book("9782070612758")
    assert book.available is False
    assert book.borrower_id == "USR002"
    assert "9782070612758" in model.find_user("USR002").borrowed_isbns
    assert repository.saved == 1
    assert view.status == ("Livre emprunté.", "success")
    assert view.actions == (True, True, "Retourner")


def test_return_selected_book() -> None:
    model, view, repository, _ = build()
    view.select_callback("9782253096337")

    view.borrow_callback()

    assert view.borrow_dialog is None
    assert model.find_book("9782253096337").available is True
    assert model.find_user("USR001").borrowed_isbns == []
    assert repository.saved == 1
    assert view.status == ("Livre retourné.", "success")


def test_borrow_without_users_shows_error() -> None:
    model, view, _, _ = build(
        model=Library(books=make_model().books, users=[])
    )
    view.select_callback("9782070612758")

    view.borrow_callback()

    assert view.borrow_dialog is None
    assert view.status[1] == "error"
