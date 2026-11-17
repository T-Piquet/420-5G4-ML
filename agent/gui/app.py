"""Entry point for the Bibliothèque CustomTkinter GUI."""

import customtkinter as ctk

from bibliotheque_api import BibliothequeAPI
from ui.shell import AppShell


def main() -> None:
    ctk.set_appearance_mode("light")
    api = BibliothequeAPI()
    app = AppShell(api)
    app.mainloop()


if __name__ == "__main__":
    main()
