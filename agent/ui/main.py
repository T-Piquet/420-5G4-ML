#!/usr/bin/env python3
"""Point d'entrée de l'interface graphique de la bibliothèque."""

import argparse
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent.parent
BUILD_DIR = AGENT_DIR / "build"
UI_DIR = Path(__file__).resolve().parent

# Le module compilé par pybind11 est généré dans le répertoire de compilation.
sys.path.insert(0, str(BUILD_DIR))
sys.path.insert(0, str(UI_DIR))

from PyQt5.QtWidgets import QApplication, QMessageBox  # noqa: E402

_service_error = None

try:
    from service import LibraryService  # noqa: E402
except ImportError as error:  # module pybind11 non compilé ou introuvable
    _service_error = error
    LibraryService = None

from theme import STYLESHEET  # noqa: E402
from window import MainWindow  # noqa: E402


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Interface graphique de gestion de bibliothèque personnelle."
    )
    parser.add_argument(
        "-d",
        "--data-dir",
        default=str(AGENT_DIR / "data"),
        help="Répertoire contenant books.txt et users.txt (défaut : agent/data).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    app = QApplication(sys.argv)
    app.setApplicationName("Bibliothèque personnelle")
    app.setStyleSheet(STYLESHEET)

    if _service_error is not None:
        QMessageBox.critical(
            None,
            "Module Python manquant",
            "Le module « bibliotheque_py » est introuvable.\n"
            "Compilez-le avec :\n\n"
            "  cmake -S . -B build\n"
            "  cmake --build build\n\n"
            f"Détail : {_service_error}",
        )
        return 1

    try:
        service = LibraryService(Path(args.data_dir))
    except FileNotFoundError as error:
        QMessageBox.critical(None, "Erreur de démarrage", str(error))
        return 1

    window = MainWindow(service)
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
