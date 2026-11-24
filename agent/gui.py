import argparse
from pathlib import Path
from tkinter import messagebox, ttk

import customtkinter as ctk

from _bibliotheque import BookSortOrder, Session


PAPER = "#f6f3ee"
SIDEBAR = "#e0dcd6"
GREEN = "#afc596"
HOVER = "#9db683"
INK = "#101c2c"


class Form(ctk.CTkToplevel):
    def __init__(self, parent, title, fields, submit):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.entries = []
        for label in fields:
            ctk.CTkLabel(self, text=label).pack(anchor="w", padx=20, pady=(10, 0))
            entry = ctk.CTkEntry(self, width=340)
            entry.pack(padx=20, pady=(0, 5))
            self.entries.append(entry)
        self.error = ctk.CTkLabel(self, text="", text_color="#a12323", wraplength=340)
        self.error.pack(padx=20)

        def confirm(_event=None):
            values = [entry.get().strip() for entry in self.entries]
            try:
                if any(not value or "|" in value for value in values):
                    raise ValueError("Remplissez tous les champs sans utiliser le caractère |.")
                submit(*values)
            except (RuntimeError, ValueError) as error:
                self.error.configure(text=str(error))
                return
            self.destroy()

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(pady=12)
        ctk.CTkButton(buttons, text="Annuler", command=self.destroy).pack(side="left", padx=6)
        ctk.CTkButton(buttons, text="Confirmer", command=confirm).pack(side="left", padx=6)
        self.bind("<Return>", confirm)
        self.bind("<Escape>", lambda _: self.destroy())
        self.wait_visibility()
        self.grab_set()
        self.entries[0].focus_set()


class BooksWindow(ctk.CTk):
    SORT_ORDERS = {
        "Ordre du catalogue": BookSortOrder.CATALOG,
        "Titre": BookSortOrder.TITLE,
        "Auteur": BookSortOrder.AUTHOR,
    }

    def __init__(self, data_dir):
        self.session = Session(data_dir)
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=PAPER)
        self.title("Bibliothèque")
        self.geometry("1200x680")
        self.minsize(980, 560)
        self.protocol("WM_DELETE_WINDOW", self.quit_and_save)

        sidebar = ctk.CTkFrame(self, width=208, corner_radius=0, fg_color=SIDEBAR)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self.nav = {}
        for name in ("Catalogue", "Utilisateurs", "Statistiques", "Sauvegardes"):
            self.nav[name] = self.button(sidebar, name, lambda name=name: self.show_page(name),
                                         outline=True, anchor="w")
            self.nav[name].pack(fill="x", padx=14, pady=(12, 0))
        self.button(sidebar, "Quitter", self.quit_and_save, outline=True).pack(
            side="bottom", fill="x", padx=14, pady=18)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)
        footer = ctk.CTkFrame(main, fg_color=PAPER, border_width=1, border_color=SIDEBAR,
                              corner_radius=0)
        footer.pack(side="bottom", fill="x")
        self.status = ctk.CTkLabel(footer, text="", anchor="w", text_color=INK,
                                   wraplength=310, justify="left")
        self.status.pack(side="left", fill="x", expand=True, padx=18)
        self.content = ctk.CTkFrame(main, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=18)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Catalog.Treeview", background=PAPER, fieldbackground=PAPER,
                        foreground=INK, rowheight=34, font=("TkDefaultFont", 12))
        style.configure("Catalog.Treeview.Heading", background="#cedbbd", foreground=INK,
                        font=("TkDefaultFont", 12, "bold"))
        style.map("Catalog.Treeview", background=[("selected", GREEN)],
                  foreground=[("selected", INK)])
        self.show_page("Catalogue")

    @staticmethod
    def button(parent, text, command, outline=False, **options):
        return ctk.CTkButton(parent, text=text, command=command, height=38, text_color=INK,
                             fg_color=PAPER if outline else GREEN, hover_color=HOVER,
                             border_color=INK, border_width=1 if outline else 0,
                             font=ctk.CTkFont(size=15, weight="bold"), **options)

    def show_page(self, name):
        for key, button in self.nav.items():
            button.configure(fg_color=GREEN if key == name else PAPER,
                             border_width=0)
        for child in self.content.winfo_children():
            child.destroy()
        self.status.configure(text="")
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text=name, text_color=INK,
                     font=ctk.CTkFont(size=38, weight="bold")).pack(side="left")
        if name == "Catalogue":
            self.catalog_page()
        elif name == "Utilisateurs":
            self.users_page(header)
        elif name == "Statistiques":
            labels = {"total": "Total des livres", "available": "Livres disponibles",
                      "borrowed": "Livres empruntés", "users": "Total des utilisateurs"}
            for key, value in self.session.statistics().items():
                ctk.CTkLabel(self.content, text=f"{labels[key]} : {value}", text_color=INK,
                             font=ctk.CTkFont(size=20)).pack(anchor="w", pady=8)
        else:
            ctk.CTkLabel(self.content, justify="left", text_color=INK, text=(
                "Sauvegarder les données écrit le catalogue et les utilisateurs sur disque.\n"
                "Créer une sauvegarde copie les fichiers déjà enregistrés en fichiers .backup."
            )).pack(anchor="w", pady=(0, 14))
            self.button(self.content, "Sauvegarder les données", self.save).pack(anchor="w", pady=6)
            self.button(self.content, "Créer une sauvegarde", self.backup, outline=True).pack(
                anchor="w", pady=6)

    def table(self, columns):
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        table = ttk.Treeview(frame, columns=tuple(columns), show="headings",
                             selectmode="browse", style="Catalog.Treeview")
        for title, width in columns.items():
            table.heading(title, text=title, anchor="w")
            table.column(title, width=width, minwidth=60, anchor="w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(side="left", fill="both", expand=True)
        table.tag_configure("alternate", background="#e7eddf")
        return table

    def catalog_page(self):
        filters = ctk.CTkFrame(self.content, fg_color="transparent")
        filters.pack(fill="x", pady=(0, 12))
        self.scope = ctk.CTkSegmentedButton(
            filters, values=["Tous les livres", "Livres disponibles"], command=self.refresh_books,
            selected_color=GREEN, selected_hover_color=HOVER, unselected_color=PAPER,
            unselected_hover_color=SIDEBAR, text_color=INK, fg_color=SIDEBAR)
        self.scope.set("Tous les livres")
        self.scope.pack(side="left")
        self.sort = ctk.CTkComboBox(filters, values=list(self.SORT_ORDERS), state="readonly",
                                     width=158, command=self.refresh_books)
        self.sort.set("Ordre du catalogue")
        self.sort.pack(side="right")
        ctk.CTkLabel(filters, text="Trier par :").pack(side="right", padx=8)

        search = ctk.CTkFrame(self.content, fg_color="transparent")
        search.pack(fill="x", pady=(0, 14))
        self.query = ctk.CTkEntry(search, placeholder_text="Rechercher par titre ou auteur", height=36)
        self.query.pack(side="left", fill="x", expand=True)
        self.query.bind("<Return>", self.refresh_books)
        self.button(search, "Ajouter un livre", self.add_book).pack(side="left", padx=10)
        self.button(search, "Rechercher", self.refresh_books).pack(side="left")
        self.book_table = self.table({"Titre": 200, "Auteur": 180, "ISBN": 120, "État": 170})
        self.book_table.bind("<<TreeviewSelect>>", self.update_actions)

        actions = ctk.CTkFrame(self.content, fg_color="transparent")
        actions.pack(fill="x", pady=(14, 0))
        self.borrow_button = self.button(actions, "Emprunter", self.borrow_book)
        self.borrow_button.pack(side="left", padx=(0, 10))
        self.return_button = self.button(actions, "Retourner", self.return_book)
        self.return_button.pack(side="left")
        self.remove_button = self.button(actions, "Supprimer le livre", self.remove_book, outline=True)
        self.remove_button.pack(side="right")
        self.refresh_books()

    def refresh_books(self, _event=None):
        try:
            rows = self.session.books(self.scope.get() == "Livres disponibles", self.query.get(),
                                      None,
                                      self.SORT_ORDERS[self.sort.get()])
        except (RuntimeError, UnicodeError) as error:
            messagebox.showerror("Catalogue", str(error), parent=self)
            return
        for item in self.book_table.get_children():
            self.book_table.delete(item)
        self.book_rows = {}
        for index, row in enumerate(rows):
            state = "Disponible" if row["available"] else f"Emprunté par : {row['borrower']}"
            item = self.book_table.insert("", "end", tags=("alternate",) if index % 2 else (),
                                          values=(row["title"], row["author"], row["isbn"], state))
            self.book_rows[item] = row
        self.update_actions()
        self.status.configure(text=f"{len(rows)} livre(s)" if rows else "Aucun livre à afficher")

    def selected_book(self):
        selection = self.book_table.selection()
        return self.book_rows.get(selection[0]) if selection else None

    def update_actions(self, _event=None):
        book = self.selected_book()
        self.borrow_button.configure(state="normal" if book and book["available"] else "disabled")
        self.return_button.configure(state="normal" if book and not book["available"] else "disabled")
        self.remove_button.configure(state="normal" if book else "disabled")

    def add_book(self):
        def submit(*values):
            self.session.add_book(*values)
            self.refresh_books()
        Form(self, "Ajouter un livre", ("Titre", "Auteur", "ISBN"), submit)

    def borrow_book(self):
        book = self.selected_book()
        if book:
            def submit(user_id):
                self.session.borrow_book(book["isbn"], user_id)
                self.refresh_books()
            Form(self, "Emprunter un livre", ("ID de l’utilisateur",), submit)

    def return_book(self):
        book = self.selected_book()
        if book and self.run_action(lambda: self.session.return_book(book["isbn"]), "Livre retourné"):
            self.refresh_books()

    def remove_book(self):
        book = self.selected_book()
        if book and messagebox.askyesno("Supprimer le livre", f"Supprimer « {book['title']} » ?", parent=self):
            if self.run_action(lambda: self.session.remove_book(book["isbn"]), "Livre supprimé"):
                self.refresh_books()

    def users_page(self, header):
        def add_user():
            def submit(*values):
                self.session.add_user(*values)
                self.show_page("Utilisateurs")
            Form(self, "Ajouter un utilisateur", ("Nom", "ID utilisateur"), submit)

        self.button(header, "Ajouter un utilisateur", add_user).pack(side="right")
        self.user_table = self.table({"Nom": 300, "ID utilisateur": 180})
        users = self.session.users()
        for index, user in enumerate(users):
            self.user_table.insert("", "end", values=(user["name"], user["id"]),
                                   tags=("alternate",) if index % 2 else ())
        self.status.configure(text=f"{len(users)} utilisateur(s)")

    def run_action(self, action, success):
        try:
            action()
        except RuntimeError as error:
            messagebox.showerror("Bibliothèque", str(error), parent=self)
            return False
        self.status.configure(text=success)
        return True

    def save(self):
        return self.run_action(self.session.save, "Données sauvegardées.")

    def backup(self):
        self.run_action(self.session.backup, "Copie de sauvegarde créée.")

    def quit_and_save(self):
        if self.save():
            self.destroy()


def main():
    parser = argparse.ArgumentParser(description="Gérer la bibliothèque avec une interface graphique.")
    parser.add_argument("--data-dir", "-d", type=Path, required=True)
    args = parser.parse_args()
    try:
        window = BooksWindow(args.data_dir)
    except RuntimeError as error:
        parser.exit(1, f"Erreur : {error}\n")
    window.mainloop()


if __name__ == "__main__":
    main()
