"""Test de fumée de la fenêtre principale.

Ce test nécessite un serveur d'affichage (X11 ou Wayland). Il est ignoré
automatiquement lorsque aucun affichage n'est disponible.
"""

import os

import pytest


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
        assert window.counter_label.cget("text") == "0"
    finally:
        window.destroy()
