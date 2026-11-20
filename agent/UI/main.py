"""Point d'entrée de l'interface graphique."""

from pathlib import Path

import customtkinter as ctk

from app import config
from app.controllers.main_controller import MainController
from app.repositories.library_repository import LibraryRepository
from app.views.main_window import MainWindow

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    """Assemble les couches et lance la boucle graphique."""
    ctk.set_appearance_mode(config.APPEARANCE_MODE)
    ctk.set_default_color_theme(config.COLOR_THEME)

    try:
        repository = LibraryRepository(DATA_DIR)
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    model = repository.load()

    view = MainWindow()
    MainController(model, view, repository)

    view.mainloop()


if __name__ == "__main__":
    main()
