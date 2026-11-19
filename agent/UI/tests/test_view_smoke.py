"""Test de fumée de la fenêtre principale.

Ce test nécessite un serveur d'affichage (X11 ou Wayland). Il est ignoré
automatiquement lorsque aucun affichage n'est disponible.
"""

import os

import pytest

from app.views.view_models import BookRow


def _display_available() -> bool:
    if os.name == "nt" or os.uname().sysname == "Darwin":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


@pytest.mark.skipif(
    not _display_available(), reason="Aucun serveur d'affichage disponible"
)
def test_main_window_smoke() -> None:
    from app.views.main_window import MainWindow

    window = MainWindow()
    try:
        window.update()

        assert window.section_title.cget("text") == "Livres"
        assert window.add_button.cget("text") == "Ajouter"
        assert window.borrow_button.cget("text") == "Emprunter"
        assert window.delete_button.cget("text") == "Supprimer"
        assert window.search_entry.cget("placeholder_text") == (
            "Rechercher par titre, auteur ou ISBN…"
        )

        window.set_books(
            [
                BookRow(
                    isbn="9782070612758",
                    title="Le Petit Prince",
                    author="Antoine de Saint-Exupéry",
                    status_label="Disponible",
                    available=True,
                )
            ]
        )
        window.set_selected("9782070612758")
        window.set_actions(
            can_delete=True, can_borrow=True, borrow_label="Emprunter"
        )
        window.set_status("Prêt.", "success")
        window.set_section("Emprunts")
        assert window.section_title.cget("text") == "Emprunts"

        window.set_section("Livres")
        assert window.section_title.cget("text") == "Livres"
    finally:
        window.destroy()
