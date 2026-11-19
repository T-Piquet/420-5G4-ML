"""Tests directs du module natif pybind11."""

import pytest

pytest.importorskip(
    "app.bibliotheque_core", reason="Module natif non compilé"
)

from app import bibliotheque_core as core


def test_book_round_trip() -> None:
    book = core.Book("Le Petit Prince", "Antoine de Saint-Exupéry", "9782070612758")

    assert book.title == "Le Petit Prince"
    assert book.author == "Antoine de Saint-Exupéry"
    assert book.isbn == "9782070612758"
    assert book.available is True
    assert book.borrower_id == ""
    assert book.to_file_format() == (
        "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|"
    )

    book.check_out("USR001")

    assert book.available is False
    assert book.borrower_id == "USR001"

    book.return_book()

    assert book.available is True
    assert book.borrower_id == ""


def test_library_operations() -> None:
    library = core.Library()
    library.add_book(core.Book("Titre", "Auteur", "ISBN-1"))
    library.add_user(core.User("Marie Dubois", "USR001"))

    assert library.find_book("ISBN-1").title == "Titre"
    assert library.find_book("inconnu") is None
    assert library.find_user("USR001").name == "Marie Dubois"
    assert library.find_user("USR999") is None

    assert library.check_out_book("ISBN-1", "USR001") is True
    assert library.find_book("ISBN-1").available is False
    assert library.find_user("USR001").borrowed_isbns == ["ISBN-1"]
    assert library.total_books() == 1
    assert library.available_count() == 0
    assert library.checked_out_count() == 1

    assert library.return_book("ISBN-1") is True
    assert library.find_book("ISBN-1").available is True
    assert library.find_user("USR001").borrowed_isbns == []

    assert library.remove_book("ISBN-1") is True
    assert library.find_book("ISBN-1") is None


def test_remove_book_detaches_isbn_from_users() -> None:
    library = core.Library()
    library.add_book(core.Book("Titre", "Auteur", "ISBN-1"))
    library.add_user(core.User("Marie Dubois", "USR001"))
    library.check_out_book("ISBN-1", "USR001")

    assert library.remove_book("ISBN-1") is True

    assert library.find_user("USR001").borrowed_isbns == []


def test_file_manager_round_trip(tmp_path) -> None:
    library = core.Library()
    library.add_book(core.Book("Titre", "Auteur", "ISBN-1"))
    library.add_user(core.User("Marie Dubois", "USR001"))

    manager = core.FileManager(
        str(tmp_path / "books.txt"),
        str(tmp_path / "users.txt"),
    )
    assert manager.save_library(library) is True

    reloaded = core.Library()
    assert manager.load_library(reloaded) is True
    assert reloaded.find_book("ISBN-1").title == "Titre"
    assert reloaded.find_user("USR001").name == "Marie Dubois"
    assert (tmp_path / "books.txt").read_text(encoding="utf-8") == (
        "Titre|Auteur|ISBN-1|1|\n"
    )
    assert (tmp_path / "users.txt").read_text(encoding="utf-8") == (
        "Marie Dubois|USR001|\n"
    )
