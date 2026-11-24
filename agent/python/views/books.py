"""Onglet Livres : recherche, tableau et ajout/suppression."""

from __future__ import annotations

from tkinter import ttk

import customtkinter as ctk

COLUMNS = ("title", "author", "isbn", "status")
COLUMN_LABELS = {
    "title": "Titre",
    "author": "Auteur",
    "isbn": "ISBN",
    "status": "Statut",
}


class BooksView(ctk.CTkFrame):
    def __init__(self, master, service, on_status, on_data_changed=None) -> None:
        super().__init__(master, fg_color="transparent")

        self.service = service
        self.on_status = on_status
        self.on_data_changed = on_data_changed

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_search_bar()
        self._build_table()
        self._build_form()

        self.refresh()

    # Construction de l'interface

    def _build_search_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text="Rechercher").grid(
            row=0, column=0, padx=(0, 8), pady=4, sticky="w"
        )

        self.search_entry = ctk.CTkEntry(
            bar, placeholder_text="Titre ou auteur"
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")
        self.search_entry.bind("<Return>", lambda _event: self._on_search())

        self.search_by = ctk.CTkOptionMenu(
            bar, values=["Titre", "Auteur"], width=110
        )
        self.search_by.grid(row=0, column=2, padx=(0, 8), pady=4)

        self.search_button = ctk.CTkButton(
            bar, text="Rechercher", width=110, command=self._on_search
        )
        self.search_button.grid(row=0, column=3, padx=(0, 12), pady=4)

        self.available_only = ctk.BooleanVar(value=False)
        self.available_checkbox = ctk.CTkCheckBox(
            bar,
            text="Disponibles seulement",
            variable=self.available_only,
            command=self._on_search,
        )
        self.available_checkbox.grid(row=0, column=4, pady=4)

    def _build_table(self) -> None:
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self._configure_tree_style()

        self.tree = ttk.Treeview(
            table_frame,
            columns=COLUMNS,
            show="headings",
            style="Livres.Treeview",
            selectmode="browse",
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)

        self.tree.heading("title", text=COLUMN_LABELS["title"])
        self.tree.heading("author", text=COLUMN_LABELS["author"])
        self.tree.heading("isbn", text=COLUMN_LABELS["isbn"])
        self.tree.heading("status", text=COLUMN_LABELS["status"])

        self.tree.column("title", width=280, minwidth=140, anchor="w", stretch=True)
        self.tree.column("author", width=180, minwidth=110, anchor="w", stretch=True)
        self.tree.column("isbn", width=140, minwidth=100, anchor="w", stretch=False)
        self.tree.column("status", width=110, minwidth=90, anchor="center", stretch=False)

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
            "Livres.Treeview",
            background=background,
            fieldbackground=background,
            foreground=foreground,
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Livres.Treeview.Heading",
            background=heading_background,
            foreground=foreground,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Livres.Treeview",
            background=[("selected", selected)],
            foreground=[("selected", "#ffffff")],
        )
        style.map(
            "Livres.Treeview.Heading",
            background=[("active", heading_background)],
        )

    def _build_form(self) -> None:
        form = ctk.CTkFrame(self)
        form.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 8))
        form.grid_columnconfigure(1, weight=3)
        form.grid_columnconfigure(3, weight=3)
        form.grid_columnconfigure(5, weight=2)

        ctk.CTkLabel(
            form,
            text="Ajouter un livre",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(form, text="Titre").grid(
            row=1, column=0, padx=(8, 6), pady=4, sticky="w"
        )
        self.title_entry = ctk.CTkEntry(form, placeholder_text="Titre du livre")
        self.title_entry.grid(row=1, column=1, padx=(0, 12), pady=4, sticky="ew")

        ctk.CTkLabel(form, text="Auteur").grid(
            row=1, column=2, padx=(0, 6), pady=4, sticky="w"
        )
        self.author_entry = ctk.CTkEntry(form, placeholder_text="Auteur")
        self.author_entry.grid(row=1, column=3, padx=(0, 12), pady=4, sticky="ew")

        ctk.CTkLabel(form, text="ISBN").grid(
            row=1, column=4, padx=(0, 6), pady=4, sticky="w"
        )
        self.isbn_entry = ctk.CTkEntry(form, placeholder_text="ISBN")
        self.isbn_entry.grid(row=1, column=5, padx=(0, 8), pady=4, sticky="ew")

        for entry in (self.title_entry, self.author_entry, self.isbn_entry):
            entry.bind("<Return>", lambda _event: self._on_add())

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=6, sticky="e", padx=8, pady=(4, 8))

        ctk.CTkButton(
            buttons, text="Ajouter", width=110, command=self._on_add
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            buttons,
            text="Supprimer la sélection",
            width=180,
            fg_color="#a33a3a",
            hover_color="#8a2f2f",
            command=self._on_delete,
        ).grid(row=0, column=1)

    # Donnees

    def _visible_books(self) -> list[dict]:
        query = self.search_entry.get().strip()
        if query:
            by = "author" if self.search_by.get() == "Auteur" else "title"
            books = self.service.search_books(query, by)
        else:
            books = self.service.get_books()

        if self.available_only.get():
            books = [book for book in books if book["available"]]
        return books

    def refresh(self) -> list[dict]:
        books = self._visible_books()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in books:
            status = "Disponible" if book["available"] else "Emprunté"
            self.tree.insert(
                "",
                "end",
                values=(
                    book["title"],
                    book["author"],
                    book["isbn"],
                    status,
                ),
            )
        return books

    # Actions

    def _on_search(self) -> None:
        books = self.refresh()
        query = self.search_entry.get().strip()
        if query:
            self.on_status(f"{len(books)} livre(s) trouvé(s) pour « {query} ».")
        else:
            self.on_status(f"{len(books)} livre(s) affiché(s).")

    def _on_add(self) -> None:
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()

        if not title or not author or not isbn:
            self.on_status("Veuillez remplir le titre, l'auteur et l'ISBN.")
            return

        try:
            book = self.service.add_book(title, author, isbn)
        except ValueError as error:
            self.on_status(str(error))
            return

        for entry in (self.title_entry, self.author_entry, self.isbn_entry):
            entry.delete(0, "end")

        self.refresh()
        self._notify_change()
        self.on_status(f"Livre ajouté : {book['title']} ({book['isbn']}).")

    def _on_delete(self) -> None:
        selection = self.tree.selection()
        if not selection:
            self.on_status("Veuillez sélectionner un livre à supprimer.")
            return

        values = self.tree.item(selection[0], "values")
        title, isbn = values[0], values[2]

        if self.service.remove_book(isbn):
            self.refresh()
            self._notify_change()
            self.on_status(f"Livre supprimé : {title} ({isbn}).")
        else:
            self.on_status(f"Impossible de supprimer le livre {isbn}.")

    def _notify_change(self) -> None:
        if self.on_data_changed is not None:
            self.on_data_changed()
