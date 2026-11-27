import customtkinter as ctk


def main() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Application de test")
    app.geometry("400x300")

    app.mainloop()


if __name__ == "__main__":
    main()
