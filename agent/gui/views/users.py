import tkinter as tk
import customtkinter as ctk
import warnings
from tkinter import messagebox

from gui.service import ServiceError


def make_trash_icon(size=20, color="#ffffff"):
    icon = tk.PhotoImage(width=size, height=size)
    icon.put(color, to=(8, 1, 12, 3))
    icon.put(color, to=(4, 3, 16, 5))
    icon.put(color, to=(5, 6, 15, 8))
    icon.put(color, to=(5, 6, 7, 18))
    icon.put(color, to=(13, 6, 15, 18))
    icon.put(color, to=(5, 16, 15, 18))
    icon.put(color, to=(8, 9, 9, 15))
    icon.put(color, to=(11, 9, 12, 15))
    return icon


class UsersView(ctk.CTkFrame):
    COLUMNS = ["Nom", "ID", "Emprunts", "ISBN empruntés"]
    WEIGHTS = [2, 1, 1, 3]

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._trash_icon = make_trash_icon()
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ctk.CTkEntry(
            top,
            textvariable=self.search_var,
            placeholder_text="Rechercher par nom ou ID...",
        ).grid(row=0, column=0, sticky="ew")

        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(container, fg_color=("gray85", "gray25"))
        header.grid(row=0, column=0, sticky="ew")
        for index, (column, weight) in enumerate(zip(self.COLUMNS, self.WEIGHTS)):
            header.grid_columnconfigure(index, weight=weight, uniform="users")
            ctk.CTkLabel(header, text=column, anchor="w").grid(
                row=0, column=index, sticky="ew", padx=8, pady=6
            )
        header.grid_columnconfigure(len(self.COLUMNS), minsize=70)

        self.rows = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.rows.grid(row=1, column=0, sticky="nsew")
        self.rows.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            container,
            text="Aucun utilisateur trouvé",
            font=ctk.CTkFont(size=16, weight="bold"),
        )

        self.refresh()

        self.add_button = ctk.CTkButton(
            self, text="Ajouter un utilisateur", command=self.open_add_dialog
        )
        self.add_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))


    def refresh(self):
        """Recharge la liste des utilisateurs filtrés."""
        query = self.search_var.get().strip().casefold()

        users = self.app.service.users
        if query:
            users = [
                user
                for user in users
                if query in user.name.casefold() or query in user.user_id.casefold()
            ]

        for child in self.rows.winfo_children():
            child.destroy()

        for index, user in enumerate(users):
            row = ctk.CTkFrame(self.rows)
            row.grid(row=index, column=0, sticky="ew", pady=2)
            for column, weight in enumerate(self.WEIGHTS):
                row.grid_columnconfigure(column, weight=weight, uniform="users")
            row.grid_columnconfigure(len(self.WEIGHTS), minsize=70)

            values = [
                user.name,
                user.user_id,
                str(user.borrowed_count),
                ", ".join(user.borrowed_books) or "-",
            ]
            for column, value in enumerate(values):
                ctk.CTkLabel(row, text=value, anchor="w").grid(
                    row=0, column=column, sticky="ew", padx=8, pady=6
                )

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="CTkButton Warning: Given image is not CTkImage",
                    category=UserWarning,
                )
                delete_button = ctk.CTkButton(
                    row,
                    text="",
                    image=self._trash_icon,
                    width=40,
                    height=30,
                    fg_color="#b33939",
                    hover_color="#8f2c2c",
                    command=lambda name=user.name, user_id=user.user_id: self.confirm_delete(
                        name, user_id
                    ),
                )
            delete_button.grid(row=0, column=len(values), padx=8, pady=4)

        if users:
            self.rows.grid()
            self.empty_label.place_forget()
        else:
            self.rows.grid_remove()
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def confirm_delete(self, name, user_id):
        """Demande confirmation avant de supprimer un utilisateur."""
        if not messagebox.askyesno(
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer l'utilisateur « {name} » ({user_id}) ?",
        ):
            return

        try:
            self.app.service.remove_user(user_id)
        except ServiceError as error:
            self.app.show_error(str(error))
            self.refresh()
            return

        self.app.mark_unsaved()
        self.app.show_success(f"Utilisateur « {name} » supprimé.")
        self.refresh()

    def open_add_dialog(self):
        """Ouvre un dialog pour ajouter un nouvel utilisateur."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajouter un utilisateur")
        dialog.geometry("420x300")
        dialog.minsize(400, 280)
        dialog.transient(self.winfo_toplevel())
        dialog.grid_columnconfigure(1, weight=1)

        name_var = tk.StringVar()
        user_id_var = tk.StringVar()

        fields = [
            ("Nom :", name_var),
            ("ID :", user_id_var),
        ]
        for row, (label, variable) in enumerate(fields):
            ctk.CTkLabel(dialog, text=label).grid(
                row=row, column=0, sticky="w", padx=(20, 10), pady=10
            )
            ctk.CTkEntry(dialog, textvariable=variable).grid(
                row=row, column=1, sticky="ew", padx=(0, 20), pady=10
            )

        def add_user():
            name = name_var.get().strip()
            try:
                self.app.service.add_user(name, user_id_var.get().strip())
            except ServiceError as error:
                self.app.show_error(str(error))
                return
            self.app.mark_unsaved()
            self.app.show_success(f"Utilisateur '{name}' ajouté avec succès.")
            self.refresh()
            dialog.destroy()

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.grid(
            row=len(fields), column=0, columnspan=2, sticky="ew", padx=20, pady=20
        )
        buttons.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(buttons, text="Annuler", command=dialog.destroy).grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        ctk.CTkButton(buttons, text="Ajouter", command=add_user).grid(
            row=0, column=1, sticky="ew"
        )

        dialog.grab_set()
