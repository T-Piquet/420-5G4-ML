"""Point d'entrée de l'interface graphique."""

import customtkinter as ctk

from app import config
from app.controllers.main_controller import MainController
from app.models.app_model import AppModel
from app.views.main_window import MainWindow


def main() -> None:
    """Assemble les couches MVC et lance la boucle graphique."""
    ctk.set_appearance_mode(config.APPEARANCE_MODE)
    ctk.set_default_color_theme(config.COLOR_THEME)

    model = AppModel()
    view = MainWindow()
    MainController(model, view)

    view.mainloop()


if __name__ == "__main__":
    main()
