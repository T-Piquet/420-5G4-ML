"""Localise et importe le module compilé `bibliotheque`."""
import importlib
import sys
from pathlib import Path
from types import ModuleType

_AGENT_DIR = Path(__file__).resolve().parents[2]
_BUILD_DIR = _AGENT_DIR / "build" / "python_bindings"

BUILD_INSTRUCTIONS = (
    "Compilez-le depuis le dossier agent/ :\n"
    "  cmake -S python_bindings -B build/python_bindings\n"
    "  cmake --build build/python_bindings"
)


class BackendUnavailableError(RuntimeError):
    """Le module C++ n'a pas été compilé ou ne peut pas être chargé."""


def load_backend() -> ModuleType:
    if str(_BUILD_DIR) not in sys.path:
        sys.path.insert(0, str(_BUILD_DIR))
    try:
        return importlib.import_module("bibliotheque")
    except ImportError as error:
        raise BackendUnavailableError(
            f"Le module C++ « bibliotheque » est introuvable ({error}).\n{BUILD_INSTRUCTIONS}"
        ) from error
