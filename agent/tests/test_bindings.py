from __future__ import annotations

from pathlib import Path

import pytest

import bibliotheque_py as biblio


def test_load_existing_data(store):
    library, _, _ = store
    assert library.get_total_books() > 0
    assert len(library.get_all_users()) > 0
    first_book = library.get_all_books()[0]
    assert first_book.title
    assert first_book.author
    assert first_book.isbn
    assert library.get_available_book_count() + library.get_checked_out_book_count() == (
        library.get_total_books()
    )


def test_add_search_and_remove_book(store):
    library, _, _ = store
    title = "Livre de test unique"
    author = "Autrice de test"
    isbn = "TEST-ISBN-0001"

    assert library.book_exists(isbn) is False
    library.add_book(biblio.Book(title, author, isbn))
    assert library.book_exists(isbn) is True

    by_title = library.search_books_by_title("test unique")
    assert [book.isbn for book in by_title] == [isbn]

    by_author = library.search_books_by_author("autrice de test")
    assert [book.isbn for book in by_author] == [isbn]

    assert library.remove_book(isbn) is True
    assert library.book_exists(isbn) is False
    assert library.remove_book(isbn) is False


def test_add_user_and_duplicate_check(store):
    library, _, _ = store
    user_id = "TEST-USER-0001"

    assert library.user_exists(user_id) is False
    library.add_user(biblio.User("Utilisatrice de test", user_id))
    assert library.user_exists(user_id) is True

    users = library.get_all_users()
    assert any(user.user_id == user_id for user in users)


def test_borrow_and_return_book(store):
    library, _, _ = store
    user_id = "TEST-USER-EMPRUNT"
    library.add_user(biblio.User("Emprunteuse de test", user_id))

    available = library.get_available_books()
    assert available
    isbn = available[0].isbn

    assert library.check_out_book(isbn, user_id) is True
    borrowed_book = next(book for book in library.get_all_books() if book.isbn == isbn)
    assert borrowed_book.is_available is False
    assert borrowed_book.borrower_id == user_id

    user = next(user for user in library.get_all_users() if user.user_id == user_id)
    assert isbn in user.borrowed_books
    assert library.check_out_book(isbn, user_id) is False

    assert library.return_book(isbn) is True
    returned_book = next(book for book in library.get_all_books() if book.isbn == isbn)
    assert returned_book.is_available is True
    assert returned_book.borrower_id == ""

    user = next(user for user in library.get_all_users() if user.user_id == user_id)
    assert isbn not in user.borrowed_books
    assert library.return_book(isbn) is False


def test_borrow_refused_for_unknown_user(store):
    library, _, _ = store
    isbn = library.get_available_books()[0].isbn
    assert library.check_out_book(isbn, "UTILISATEUR-INCONNU") is False


def test_save_and_reload_roundtrip(store):
    library, file_manager, data_dir = store
    isbn = "TEST-ISBN-PERSIST"
    user_id = "TEST-USER-PERSIST"
    library.add_book(biblio.Book("Livre persistant", "Auteur persistant", isbn))
    library.add_user(biblio.User("Utilisateur persistant", user_id))

    assert file_manager.save_library_data(library) is True

    reloaded = biblio.Library()
    reloaded_manager = biblio.FileManager(
        str(data_dir / "books.txt"), str(data_dir / "users.txt")
    )
    assert reloaded_manager.load_library_data(reloaded) is True
    assert reloaded.book_exists(isbn) is True
    assert reloaded.user_exists(user_id) is True

    book_line = next(
        line for line in (data_dir / "books.txt").read_text().splitlines()
        if isbn in line
    )
    assert book_line == f"Livre persistant|Auteur persistant|{isbn}|1|"


def test_create_backup_and_existing_backup_error(store):
    _, file_manager, data_dir = store
    file_manager.create_backup()

    assert Path(f"{data_dir / 'books.txt'}.backup").exists()
    assert Path(f"{data_dir / 'users.txt'}.backup").exists()

    # Comportement C++ existant : une deuxieme sauvegarde leve une exception
    # car filesystem::copy_file refuse d'ecraser la destination.
    with pytest.raises(RuntimeError):
        file_manager.create_backup()
