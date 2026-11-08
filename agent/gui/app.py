"""Assemble le modèle, la fenêtre et le contrôleur."""
from pathlib import Path

from gui.controllers.app_controller import AppController
from gui.models.library_model import LibraryModel
from gui.views.main_window import MainWindow


def create_app(data_dir: Path) -> tuple[MainWindow, AppController]:
    model = LibraryModel(data_dir)
    window = MainWindow()
    return window, AppController(model, window)
