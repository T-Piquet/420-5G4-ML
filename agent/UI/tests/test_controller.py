"""Tests du contrôleur avec une vue factice, sans Tkinter."""

from app.controllers.main_controller import MainController
from app.models.app_model import AppModel


class FakeView:
    """Vue minimale qui enregistre les appels du contrôleur."""

    def __init__(self) -> None:
        self.message: str | None = None
        self.counter: int | None = None
        self.increment_callback = None

    def set_message(self, message: str) -> None:
        self.message = message

    def set_counter(self, value: int) -> None:
        self.counter = value

    def set_increment_callback(self, callback) -> None:
        self.increment_callback = callback


def test_controller_initializes_view() -> None:
    model = AppModel(message="Bonjour", counter=3)
    view = FakeView()

    MainController(model, view)

    assert view.message == "Bonjour"
    assert view.counter == 3
    assert view.increment_callback is not None


def test_controller_increment_updates_model_and_view() -> None:
    model = AppModel()
    view = FakeView()
    MainController(model, view)

    assert view.increment_callback is not None
    view.increment_callback()

    assert model.counter == 1
    assert view.counter == 1

    view.increment_callback()

    assert model.counter == 2
    assert view.counter == 2
