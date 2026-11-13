"""Onglet Utilisateurs : tableau et ajout d'utilisateurs."""

from __future__ import annotations

from tkinter import ttk

import customtkinter as ctk

COLUMNS = ("name", "user_id", "borrowed_count", "borrowed_books")
COLUMN_LABELS = {
    "name": "Nom",
    "user_id": "ID",
    "borrowed_count": "Nb empruntés",
    "borrowed_books": "ISBNs",
}


class UsersView(ctk.CTkFrame):
    def __init__(self, master, service, on_status) -> None:
        super().__init__(master, fg_color="transparent")

        self.service = service
        self.on_status = on_status

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_table()
        self._build_form()

        self.refresh()

    # Construction de l'interface

    def _build_table(self) -> None:
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=4)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self._configure_tree_style()

        self.tree = ttk.Treeview(
            table_frame,
            columns=COLUMNS,
            show="headings",
            style="Utilisateurs.Treeview",
            selectmode="browse",
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)

        self.tree.heading("name", text=COLUMN_LABELS["name"])
        self.tree.heading("user_id", text=COLUMN_LABELS["user_id"])
        self.tree.heading("borrowed_count", text=COLUMN_LABELS["borrowed_count"])
        self.tree.heading("borrowed_books", text=COLUMN_LABELS["borrowed_books"])

        self.tree.column("name", width=240, minwidth=130, anchor="w", stretch=True)
        self.tree.column("user_id", width=140, minwidth=100, anchor="w", stretch=False)
        self.tree.column(
            "borrowed_count", width=110, minwidth=90, anchor="center", stretch=False
        )
        self.tree.column(
            "borrowed_books", width=300, minwidth=150, anchor="w", stretch=True
        )

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=6)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _configure_tree_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        if ctk.get_appearance_mode() == "Dark":
            background = "#2b2b2b"
            foreground = "#dce4ee"
            heading_background = "#1f1f1f"
            selected = "#1f538d"
        else:
            background = "#ffffff"
            foreground = "#1a1a1a"
            heading_background = "#e5e5e5"
            selected = "#3a7ebf"

        style.configure(
            "Utilisateurs.Treeview",
            background=background,
            fieldbackground=background,
            foreground=foreground,
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Utilisateurs.Treeview.Heading",
            background=heading_background,
            foreground=foreground,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Utilisateurs.Treeview",
            background=[("selected", selected)],
            foreground=[("selected", "#ffffff")],
        )
        style.map(
            "Utilisateurs.Treeview.Heading",
            background=[("active", heading_background)],
        )

    def _build_form(self) -> None:
        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            form,
            text="Ajouter un utilisateur",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(form, text="Nom").grid(
            row=1, column=0, padx=(8, 6), pady=4, sticky="w"
        )
        self.name_entry = ctk.CTkEntry(form, placeholder_text="Nom de l'utilisateur")
        self.name_entry.grid(row=1, column=1, padx=(0, 12), pady=4, sticky="ew")

        ctk.CTkLabel(form, text="ID").grid(
            row=1, column=2, padx=(0, 6), pady=4, sticky="w"
        )
        self.user_id_entry = ctk.CTkEntry(form, placeholder_text="Identifiant")
        self.user_id_entry.grid(row=1, column=3, padx=(0, 8), pady=4, sticky="ew")

        for entry in (self.name_entry, self.user_id_entry):
            entry.bind("<Return>", lambda _event: self._on_add())

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=4, sticky="e", padx=8, pady=(4, 8))

        ctk.CTkButton(
            buttons, text="Ajouter", width=110, command=self._on_add
        ).grid(row=0, column=0)

    # Donnees

    def refresh(self) -> list[dict]:
        users = self.service.get_users()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for user in users:
            self.tree.insert(
                "",
                "end",
                values=(
                    user["name"],
                    user["user_id"],
                    user["borrowed_count"],
                    ", ".join(user["borrowed_books"]),
                ),
            )
        return users

    # Actions

    def _on_add(self) -> None:
        name = self.name_entry.get().strip()
        user_id = self.user_id_entry.get().strip()

        if not name or not user_id:
            self.on_status("Veuillez remplir le nom et l'ID.")
            return

        try:
            user = self.service.add_user(name, user_id)
        except ValueError as error:
            self.on_status(str(error))
            return

        self.name_entry.delete(0, "end")
        self.user_id_entry.delete(0, "end")

        self.refresh()
        self.on_status(f"Utilisateur ajouté : {user['name']} ({user['user_id']}).")
