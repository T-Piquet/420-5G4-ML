"""Tests de la lecture et de l'écriture des données."""

from pathlib import Path

from app.models.book import Book
from app.models.library import Library
from app.models.user import User
from app.repositories.library_repository import LibraryRepository


def write_sample(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "books.txt").write_text(
        "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|\n"
        "Les Misérables|Victor Hugo|9782253096337|0|USR001\n",
        encoding="utf-8",
    )
    (data_dir / "users.txt").write_text(
        "Marie Dubois|USR001|9782253096337\n"
        "Jean Martin|USR002|\n",
        encoding="utf-8",
    )


def test_load_reads_books_and_users(tmp_path: Path) -> None:
    write_sample(tmp_path)

    library = LibraryRepository(tmp_path).load()

    assert [book.isbn for book in library.books] == [
        "9782070612758",
        "9782253096337",
    ]
    assert library.books[0].title == "Le Petit Prince"
    assert library.books[0].available is True
    assert library.books[1].available is False
    assert library.books[1].borrower_id == "USR001"
    assert library.find_user("USR001").borrowed_isbns == ["9782253096337"]
    assert library.find_user("USR002").borrowed_isbns == []


def test_load_missing_files_returns_empty_library(tmp_path: Path) -> None:
    library = LibraryRepository(tmp_path).load()

    assert library.books == []
    assert library.users == []


def test_load_ignores_incomplete_lines(tmp_path: Path) -> None:
    (tmp_path / "books.txt").write_text(
        "Titre sans ISBN|Auteur\n"
        "Bon livre|Bon auteur|123|1|\n",
        encoding="utf-8",
    )
    (tmp_path / "users.txt").write_text(
        "Utilisateur sans identifiant\n"
        "Nom valide|U1|\n",
        encoding="utf-8",
    )

    library = LibraryRepository(tmp_path).load()

    assert [book.isbn for book in library.books] == ["123"]
    assert [user.user_id for user in library.users] == ["U1"]


def test_save_round_trip(tmp_path: Path) -> None:
    library = Library(
        books=[
            Book("Le Petit Prince", "Antoine de Saint-Exupéry", "9782070612758"),
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
    repository = LibraryRepository(tmp_path)

    repository.save(library)

    assert (tmp_path / "books.txt").read_text(encoding="utf-8") == (
        "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|\n"
        "Les Misérables|Victor Hugo|9782253096337|0|USR001\n"
    )
    assert (tmp_path / "users.txt").read_text(encoding="utf-8") == (
        "Marie Dubois|USR001|9782253096337\n"
        "Jean Martin|USR002|\n"
    )

    reloaded = repository.load()
    assert reloaded.find_book("9782253096337").borrower_id == "USR001"
    assert reloaded.find_user("USR001").borrowed_isbns == ["9782253096337"]


def test_save_creates_missing_directory(tmp_path: Path) -> None:
    repository = LibraryRepository(tmp_path / "donnees")

    repository.save(Library())

    assert (tmp_path / "donnees" / "books.txt").exists()
    assert (tmp_path / "donnees" / "users.txt").exists()
