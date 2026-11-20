import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
DOSSIER_BUILD = RACINE / "build"
if DOSSIER_BUILD.is_dir() and str(DOSSIER_BUILD) not in sys.path:
    sys.path.insert(0, str(DOSSIER_BUILD))

from gui.application import ApplicationBibliotheque
from gui.controleur import ControleurBibliotheque



def analyser_arguments(argv=None):
    analyseur = argparse.ArgumentParser(
        description="Interface graphique de gestion de bibliothèque personnelle"
    )
    analyseur.add_argument(
        "-d",
        "--data-dir",
        default=str(RACINE / "data"),
        help="Répertoire contenant books.txt et users.txt (défaut : data)",
    )
    return analyseur.parse_args(argv)


def main(argv=None) -> int:
    args = analyser_arguments(argv)
    try:
        controleur = ControleurBibliotheque(args.data_dir)
    except FileNotFoundError as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1

    app = ApplicationBibliotheque(controleur)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
