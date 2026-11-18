"""Contrôleur principal : relie le modèle à la vue."""

from app.models.app_model import AppModel
from app.views.main_window import MainWindow


class MainController:
    """Traduit les actions de la vue en opérations sur le modèle."""

    def __init__(self, model: AppModel, view: MainWindow) -> None:
        self.model = model
        self.view = view

        self.view.set_increment_callback(self.on_increment)
        self.view.set_message(self.model.message)
        self.view.set_counter(self.model.counter)

    def on_increment(self) -> None:
        """Incrémente le modèle puis met la vue à jour."""
        value = self.model.increment()
        self.view.set_counter(value)
