from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

AGENT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = AGENT_DIR / "data"
BINARY = AGENT_DIR / "build" / "bibliotheque"


def hashes(directory: Path) -> dict[str, str]:
    return {
        name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
        for name in ("books.txt", "users.txt")
    }


@pytest.mark.skipif(not BINARY.exists(), reason="binaire console non compile")
def test_console_still_works_without_touching_tracked_data(tmp_path: Path):
    for name in ("books.txt", "users.txt"):
        shutil.copy2(DATA_DIR / name, tmp_path / name)

    before = hashes(tmp_path)
    result = subprocess.run(
        [str(BINARY), "-d", str(tmp_path)],
        input="0\n",
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Charg" in result.stdout
    # Le CLI recharge puis reecrit les memes donnees a la sortie.
    assert hashes(tmp_path) == before
