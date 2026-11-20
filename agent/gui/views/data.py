import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox


class DataView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Données et sauvegarde",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        self.path_label = ctk.CTkLabel(self, text="", anchor="w")
        self.path_label.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        directory_frame = ctk.CTkFrame(self)
        directory_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        directory_frame.grid_columnconfigure(0, weight=1)

        self.dir_var = tk.StringVar()
        ctk.CTkEntry(directory_frame, textvariable=self.dir_var).grid(
            row=0, column=0, sticky="ew", padx=10, pady=10
        )
        ctk.CTkButton(
            directory_frame,
            text="Changer de dossier",
            command=self.change_dir,
        ).grid(row=0, column=1, padx=(0, 10), pady=10)

        actions = ctk.CTkFrame(self)
        actions.grid(row=3, column=0, sticky="ew", padx=15, pady=10)
        actions.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(
            actions, text="Recharger", command=self.reload
        ).grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)
        ctk.CTkButton(
            actions, text="Sauvegarder", command=self.save
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        ctk.CTkButton(
            actions, text="Créer une sauvegarde", command=self.backup
        ).grid(row=0, column=2, sticky="ew", padx=(5, 10), pady=10)

        self.refresh()

    def refresh(self):
        current = str(self.app.service.data_dir)
        self.path_label.configure(text=f"Dossier de données : {current}")
        self.dir_var.set(current)

    def change_dir(self):
        new_dir = self.dir_var.get().strip()
        if not new_dir:
            self.app.show_error("Le répertoire de données est requis.")
            return
        if self.app.unsaved and not messagebox.askyesno(
            "Modifications non sauvegardées",
            "Les modifications non sauvegardées seront perdues.\nContinuer ?",
        ):
            return
        if self.app.change_data_dir(new_dir):
            self.refresh()

    def reload(self):
        self.app.reload_data()

    def save(self):
        self.app.save_data()

    def backup(self):
        self.app.backup_data()
