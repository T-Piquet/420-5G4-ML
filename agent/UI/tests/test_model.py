"""Tests du modèle applicatif."""

from app.models.app_model import AppModel


def test_initial_state() -> None:
    model = AppModel()

    assert model.message
    assert model.counter == 0


def test_increment_returns_new_value() -> None:
    model = AppModel()

    assert model.increment() == 1
    assert model.counter == 1

    assert model.increment() == 2
    assert model.counter == 2
