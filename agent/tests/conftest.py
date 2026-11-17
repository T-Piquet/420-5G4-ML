from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import pytest

AGENT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = AGENT_DIR / "data"
BUILD_PYTHON_DIR = AGENT_DIR / "build" / "python"

# Permet de lancer pytest sans definir PYTHONPATH a la main.
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))
if BUILD_PYTHON_DIR.is_dir() and str(BUILD_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_PYTHON_DIR))

import bibliotheque_py  # noqa: E402


def tracked_data_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest()
        for name in ("books.txt", "users.txt")
    }


@pytest.fixture(scope="session", autouse=True)
def guard_tracked_data():
    """Echoue si un test a ecrit dans les vrais fichiers de donnees."""
    before = tracked_data_hashes()
    yield
    after = tracked_data_hashes()
    assert after == before, (
        "Les fichiers agent/data/books.txt ou users.txt ont ete modifies "
        "pendant les tests. Utilisez toujours une copie temporaire."
    )


@pytest.fixture
def temp_data(tmp_path: Path) -> Path:
    for name in ("books.txt", "users.txt"):
        shutil.copy2(DATA_DIR / name, tmp_path / name)
    return tmp_path


@pytest.fixture
def store(temp_data: Path):
    library = bibliotheque_py.Library()
    file_manager = bibliotheque_py.FileManager(
        str(temp_data / "books.txt"), str(temp_data / "users.txt")
    )
    assert file_manager.load_library_data(library) is True
    return library, file_manager, temp_data
