import customtkinter as ctk

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650


class MainWindow(ctk.CTk):
    """Fenêtre principale de l'application de gestion de bibliothèque."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Gestion de bibliothèque")
        self.minsize(800, 500)
        self._center_window()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        welcome = ctk.CTkLabel(
            self,
            text="Bienvenue dans votre bibliothèque personnelle",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        welcome.grid(row=0, column=0, padx=24, pady=24)

    def _center_window(self) -> None:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
