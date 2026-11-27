import customtkinter as ctk

from maquette.window import LibraryApp


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = LibraryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
