#!/usr/bin/env python3
"""Lance l'interface graphique de la bibliothèque."""
import argparse
import sys
from pathlib import Path

from gui.models.backend import BackendUnavailableError

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> int:
    parser = argparse.ArgumentParser(description="Interface graphique de la bibliothèque.")
    parser.add_argument("-d", "--data-dir", type=Path, default=_DEFAULT_DATA_DIR,
                        help="dossier contenant books.txt et users.txt")
    args = parser.parse_args()
    if not args.data_dir.is_dir():
        parser.error(f"le répertoire {args.data_dir} n'existe pas")

    from gui.app import create_app

    try:
        window, _controller = create_app(args.data_dir)
    except BackendUnavailableError as error:
        print(error, file=sys.stderr)
        return 1
    window.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
