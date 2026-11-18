from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
REPERTOIRE_DONNEES = RACINE / "data"
REPERTOIRE_BUILD = RACINE / "build"

sys.path.insert(0, str(REPERTOIRE_BUILD))

PYTHON_VENV = RACINE / "gui" / ".venv" / "bin" / "python"

COMMANDE_COMPILATION = (
    f'cmake -S "{RACINE}" -B "{REPERTOIRE_BUILD}" -DBUILD_PYTHON_MODULE=ON '
    f'-DPython_EXECUTABLE="{PYTHON_VENV}" '
    f'&& cmake --build "{REPERTOIRE_BUILD}" -j'
)


def _resoudre_repertoire(repertoire_donnees=None):
    return Path(repertoire_donnees) if repertoire_donnees is not None else REPERTOIRE_DONNEES


def charger_bibliotheque(repertoire_donnees=None):
    import bibliotheque_py

    return bibliotheque_py.load_library(str(_resoudre_repertoire(repertoire_donnees)))


def sauvegarder_bibliotheque(bibliotheque, repertoire_donnees=None):
    import bibliotheque_py

    return bibliotheque_py.save_library(
        bibliotheque,
        str(_resoudre_repertoire(repertoire_donnees)),
    )


def creer_backup(repertoire_donnees=None):
    import bibliotheque_py

    return bibliotheque_py.create_backup(str(_resoudre_repertoire(repertoire_donnees)))
