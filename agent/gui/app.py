import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
from gui.service import LibraryService, ServiceError
from gui.views.books import BooksView
from gui.views.users import UsersView
from gui.views.borrows import BorrowsView
from gui.views.dashboard import DashboardView
from gui.views.stats import StatsView
from gui.views.data import DataView


class App(ctk.CTk):
    def __init__(self, data_dir):
        super().__init__()
        self.title("Bibliothèque")
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.unsaved = False
        self.service = LibraryService(data_dir)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(self, text="", anchor="w")
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)

        self.frames = {}
        for name, view_class in (
            ("Tableau de bord", DashboardView),
            ("Livres", BooksView),
            ("Utilisateurs", UsersView),
            ("Emprunts", BorrowsView),
            ("Statistiques", StatsView),
            ("Données", DataView),
        ):
            frame = view_class(self.content, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame
            ctk.CTkButton(
                self.sidebar,
                text=name,
                command=lambda n=name: self.show_frame(n),
            ).pack(padx=10, pady=5)
        self.show_frame("Tableau de bord")

    def show_frame(self, name):
        frame = self.frames[name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()
        self.status.configure(
            text=f"Page actuelle : {name}", text_color=("gray14", "gray84")
        )

    def show_books(self):
        self.show_frame("Livres")

    def reload_data(self):
        try:
            self.service.reload_library_data()
        except ServiceError as error:
            self.show_error(str(error))
            return False
        self.unsaved = False
        self.refresh_all()
        self.show_success("Données rechargées depuis le disque.")
        return True

    def save_data(self):
        try:
            self.service.save_library_data()
        except ServiceError as error:
            self.show_error(str(error))
            return False
        self.unsaved = False
        self.show_success("Données sauvegardées.")
        return True

    def backup_data(self):
        try:
            self.service.backup_library_data()
        except ServiceError as error:
            self.show_error(str(error))
            return False
        self.show_success("Sauvegarde .backup créée.")
        return True

    def change_data_dir(self, new_dir):
        path = Path(new_dir)
        if not path.is_dir():
            self.show_error(f"Le répertoire de données {path} n'existe pas.")
            return False
        try:
            self.service = LibraryService(path)
        except ServiceError as error:
            self.show_error(str(error))
            return False
        self.unsaved = False
        self.refresh_all()
        self.show_success(f"Dossier de données : {path}")
        return True

    def refresh_all(self):
        for frame in self.frames.values():
            if hasattr(frame, "refresh"):
                frame.refresh()

    def show_success(self, message):
        self.status.configure(text=message, text_color="green")

    def show_error(self, message):
        self.status.configure(text=message, text_color="red")

    def mark_unsaved(self):
        self.unsaved = True
        self.status.configure(
            text="Modifications non sauvegardées", text_color="orange"
        )

    def on_close(self):
        try:
            self.service.save_library_data()
            self.unsaved = False
        except ServiceError as error:
            if not messagebox.askyesno(
                "Erreur de sauvegarde",
                f"{error}\n\nQuitter sans sauvegarder ?",
            ):
                return
        self.destroy()
