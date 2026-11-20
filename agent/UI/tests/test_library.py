"""Tests du modèle de bibliothèque."""

import pytest

pytest.importorskip(
    "app.bibliotheque_core", reason="Module natif non compilé"
)

from app.models.book import Book
from app.models.library import Library, LibraryError, LibraryStats
from app.models.user import User


def make_library() -> Library:
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


def test_search_ignores_case_and_accents() -> None:
    library = make_library()

    assert [book.isbn for book in library.filtered_books("etranger")] == [
        "9782070360024"
    ]
    assert [book.isbn for book in library.filtered_books("EXUPERY")] == [
        "9782070612758"
    ]
    assert len(library.filtered_books("")) == 3


def test_search_matches_isbn() -> None:
    library = make_library()

    assert [book.isbn for book in library.filtered_books("9782253096337")] == [
        "9782253096337"
    ]


def test_add_book_strips_fields() -> None:
    library = make_library()

    book = library.add_book("  Germinal  ", " Émile Zola ", "9782253004226")

    assert book.title == "Germinal"
    assert book.author == "Émile Zola"
    assert library.find_book("9782253004226") == book


def test_add_book_rejects_duplicate_isbn() -> None:
    library = make_library()

    with pytest.raises(LibraryError, match="existe déjà"):
        library.add_book("Autre titre", "Autre auteur", "9782070612758")


@pytest.mark.parametrize(
    ("title", "author", "isbn"),
    [
        ("", "Auteur", "123"),
        ("Titre", "", "123"),
        ("Titre", "Auteur", ""),
        ("Titre|interdit", "Auteur", "123"),
    ],
)
def test_add_book_rejects_invalid_values(
    title: str, author: str, isbn: str
) -> None:
    library = make_library()

    with pytest.raises(LibraryError):
        library.add_book(title, author, isbn)


def test_borrow_book_updates_book_and_user() -> None:
    library = make_library()

    book = library.borrow("9782070612758", "USR002")

    assert book.available is False
    assert book.borrower_id == "USR002"
    assert "9782070612758" in library.find_user("USR002").borrowed_isbns


def test_borrow_unavailable_book_is_rejected() -> None:
    library = make_library()

    with pytest.raises(LibraryError, match="déjà emprunté"):
        library.borrow("9782253096337", "USR002")


def test_borrow_unknown_user_is_rejected() -> None:
    library = make_library()

    with pytest.raises(LibraryError, match="Utilisateur introuvable"):
        library.borrow("9782070612758", "USR999")


def test_return_book_clears_borrower() -> None:
    library = make_library()

    book = library.return_book("9782253096337")

    assert book.available is True
    assert book.borrower_id == ""
    assert "9782253096337" not in library.find_user("USR001").borrowed_isbns


def test_return_available_book_is_rejected() -> None:
    library = make_library()

    with pytest.raises(LibraryError, match="déjà disponible"):
        library.return_book("9782070612758")


def test_remove_book_detaches_it_from_users() -> None:
    library = make_library()

    library.remove_book("9782253096337")

    assert library.find_book("9782253096337") is None
    assert library.find_user("USR001").borrowed_isbns == []


def test_statistics() -> None:
    library = make_library()

    assert library.statistics() == LibraryStats(
        total=3,
        available=2,
        borrowed=1,
        users=2,
    )


def test_add_user_strips_fields() -> None:
    library = make_library()

    user = library.add_user("  Sophie Lemaire  ", " USR003 ")

    assert user.name == "Sophie Lemaire"
    assert user.user_id == "USR003"
    assert user.borrowed_isbns == []
    assert library.find_user("USR003") == user


def test_add_user_rejects_duplicate_id() -> None:
    library = make_library()

    with pytest.raises(LibraryError, match="existe déjà"):
        library.add_user("Autre", "USR001")


@pytest.mark.parametrize(
    ("name", "user_id"),
    [
        ("", "USR003"),
        ("Sophie Lemaire", ""),
        ("Nom|interdit", "USR003"),
        ("Sophie Lemaire", "USR|003"),
    ],
)
def test_add_user_rejects_invalid_values(name: str, user_id: str) -> None:
    library = make_library()

    with pytest.raises(LibraryError):
        library.add_user(name, user_id)


def test_user_search_ignores_case_and_accents() -> None:
    library = make_library()
    library.add_user("Élodie Müller", "USR003")

    assert [user.user_id for user in library.filtered_users("elodie")] == [
        "USR003"
    ]
    assert [user.user_id for user in library.filtered_users("MULLER")] == [
        "USR003"
    ]
    assert [user.user_id for user in library.filtered_users("usr001")] == [
        "USR001"
    ]
    assert len(library.filtered_users("")) == 3
