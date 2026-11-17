from __future__ import annotations

import os
from pathlib import Path

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("DISPLAY"),
    reason="Un serveur X11 (DISPLAY) est necessaire pour tester la fenetre Tk.",
)


def test_gui_workflow(temp_data: Path, monkeypatch):
    pytest.importorskip("customtkinter")
    app_module = pytest.importorskip("gui.app")

    # Evite les boites de dialogue modales pendant le scenario automatise.
    monkeypatch.setattr(app_module.messagebox, "askyesno", lambda *args, **kwargs: True)

    app = app_module.BibliothequeApp(temp_data)
    try:
        app.update_idletasks()
        assert "Livres :" in app.stats_label.cget("text")
        assert len(app.books_tree.get_children()) > 0
        assert len(app.users_tree.get_children()) > 0

        # Ajout puis suppression d'un livre via l'interface.
        remove_isbn = "GUI-ISBN-A-SUPPRIMER"
        app.new_title.insert(0, "Livre GUI a supprimer")
        app.new_author.insert(0, "Auteur GUI")
        app.new_isbn.insert(0, remove_isbn)
        app._add_book()
        assert app.library.book_exists(remove_isbn) is True

        item = next(
            row
            for row in app.books_tree.get_children()
            if app.books_tree.item(row, "values")[2] == remove_isbn
        )
        app.books_tree.selection_set(item)
        app._remove_selected_book()
        assert app.library.book_exists(remove_isbn) is False

        # Ajout d'un livre empruntable et d'un utilisateur.
        borrow_isbn = "GUI-ISBN-EMPRUNT"
        user_id = "GUI-USER-0001"
        app.new_title.insert(0, "Livre GUI emprunt")
        app.new_author.insert(0, "Auteur GUI")
        app.new_isbn.insert(0, borrow_isbn)
        app._add_book()
        assert app.library.book_exists(borrow_isbn) is True

        app.new_user_name.insert(0, "Utilisateur GUI")
        app.new_user_id.insert(0, user_id)
        app._add_user()
        assert app.library.user_exists(user_id) is True

        # Emprunt puis retour via l'interface.
        app.borrow_isbn.insert(0, borrow_isbn)
        app.user_menu.set(user_id)
        app._borrow_book()
        borrowed = next(
            book for book in app.library.get_all_books() if book.isbn == borrow_isbn
        )
        assert borrowed.is_available is False
        assert borrowed.borrower_id == user_id

        app.return_isbn.insert(0, borrow_isbn)
        app._return_book()
        returned = next(
            book for book in app.library.get_all_books() if book.isbn == borrow_isbn
        )
        assert returned.is_available is True

        # Sauvegarde dans le repertoire temporaire, puis rechargement.
        assert app._save_data() is True
        reloaded = app_module.biblio.Library()
        reloaded_manager = app_module.biblio.FileManager(
            str(temp_data / "books.txt"), str(temp_data / "users.txt")
        )
        assert reloaded_manager.load_library_data(reloaded) is True
        assert reloaded.book_exists(borrow_isbn) is True
        assert reloaded.user_exists(user_id) is True

        app._create_backup()
        assert (temp_data / "books.txt.backup").exists()
        assert (temp_data / "users.txt.backup").exists()
    finally:
        app.destroy()
