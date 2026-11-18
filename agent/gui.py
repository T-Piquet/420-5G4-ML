import sys
import os
import customtkinter as ctk

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.join(_here, "build"))

import bibliotheque


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bibliotheque")
        self.geometry("800x600")

        self.library = bibliotheque.Library()
        self.file_manager = bibliotheque.FileManager(
            os.path.join(_here, "data", "books.txt"),
            os.path.join(_here, "data", "users.txt"),
        )
        self.file_manager.loadLibraryData(self.library)

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(self, width=220)
        left.grid(row=0, column=0, sticky="ns", padx=8, pady=8)

        self.output = ctk.CTkTextbox(self)
        self.output.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=8)
        self.output.configure(state="disabled")

        ctk.CTkLabel(left, text="ISBN").pack()
        self.isbn = ctk.CTkEntry(left)
        self.isbn.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(left, text="Titre").pack()
        self.title_entry = ctk.CTkEntry(left)
        self.title_entry.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(left, text="Auteur").pack()
        self.author = ctk.CTkEntry(left)
        self.author.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(left, text="ID utilisateur").pack()
        self.user_id = ctk.CTkEntry(left)
        self.user_id.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(left, text="Nom utilisateur").pack()
        self.user_name = ctk.CTkEntry(left)
        self.user_name.pack(fill="x", pady=(0, 10))

        buttons = [
            ("Ajouter livre",         self._add_book),
            ("Supprimer livre",       self._remove_book),
            ("Recherche par titre",   self._search_title),
            ("Recherche par auteur",  self._search_author),
            ("Tous les livres",       self._all_books),
            ("Livres disponibles",    self._available_books),
            ("Ajouter utilisateur",   self._add_user),
            ("Tous les utilisateurs", self._all_users),
            ("Emprunter",             self._borrow),
            ("Retourner",             self._return),
            ("Statistiques",          self._stats),
            ("Sauvegarder",           self._save),
        ]

        for label, cmd in buttons:
            ctk.CTkButton(left, text=label, command=cmd).pack(fill="x", pady=2)

    def _print(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def _add_book(self):
        title = self.title_entry.get().strip()
        author = self.author.get().strip()
        isbn = self.isbn.get().strip()
        if not title or not author or not isbn:
            self._print("Erreur: titre, auteur et ISBN requis.")
            return
        if self.library.findBookByISBN(isbn):
            self._print(f"Erreur: ISBN {isbn} existe deja.")
            return
        self.library.addBook(bibliotheque.Book(title, author, isbn))
        self._print(f"Livre ajoute: {title}")

    def _remove_book(self):
        isbn = self.isbn.get().strip()
        if not isbn:
            self._print("Erreur: ISBN requis.")
            return
        if self.library.removeBook(isbn):
            self._print(f"Livre {isbn} supprime.")
        else:
            self._print(f"Erreur: livre {isbn} introuvable.")

    def _search_title(self):
        results = self.library.searchBooksByTitle(self.title_entry.get().strip())
        self._print_books(results)

    def _search_author(self):
        results = self.library.searchBooksByAuthor(self.author.get().strip())
        self._print_books(results)

    def _all_books(self):
        self._print_books(self.library.getAllBooks())

    def _available_books(self):
        self._print_books(self.library.getAvailableBooks())

    def _print_books(self, books):
        if not books:
            self._print("Aucun livre.")
            return
        lines = ""
        for b in books:
            status = "disponible" if b.getAvailability() else f"emprunte par {b.getBorrowerId()}"
            lines += f"{b.getTitle()} | {b.getAuthor()} | {b.getISBN()} | {status}\n"
        self._print(lines)

    def _add_user(self):
        name = self.user_name.get().strip()
        uid = self.user_id.get().strip()
        if not name or not uid:
            self._print("Erreur: nom et ID requis.")
            return
        if self.library.findUserById(uid):
            self._print(f"Erreur: ID {uid} existe deja.")
            return
        self.library.addUser(bibliotheque.User(name, uid))
        self._print(f"Utilisateur ajoute: {name}")

    def _all_users(self):
        users = self.library.getAllUsers()
        if not users:
            self._print("Aucun utilisateur.")
            return
        lines = ""
        for u in users:
            borrowed = ", ".join(u.getBorrowedBooks()) if u.getBorrowedBooks() else "aucun"
            lines += f"{u.getName()} | {u.getUserId()} | emprunts: {borrowed}\n"
        self._print(lines)

    def _borrow(self):
        isbn = self.isbn.get().strip()
        uid = self.user_id.get().strip()
        if not isbn or not uid:
            self._print("Erreur: ISBN et ID requis.")
            return
        if self.library.checkOutBook(isbn, uid):
            self._print(f"Livre {isbn} emprunte par {uid}.")
        else:
            self._print("Erreur: emprunt impossible.")

    def _return(self):
        isbn = self.isbn.get().strip()
        if not isbn:
            self._print("Erreur: ISBN requis.")
            return
        if self.library.returnBook(isbn):
            self._print(f"Livre {isbn} retourne.")
        else:
            self._print("Erreur: retour impossible.")

    def _stats(self):
        self._print(
            f"Total livres: {self.library.getTotalBooks()}\n"
            f"Disponibles: {self.library.getAvailableBookCount()}\n"
            f"Empruntes: {self.library.getCheckedOutBookCount()}\n"
            f"Utilisateurs: {len(self.library.getAllUsers())}\n"
        )

    def _save(self):
        if self.file_manager.saveLibraryData(self.library):
            self._print("Sauvegarde effectuee.")
        else:
            self._print("Erreur lors de la sauvegarde.")

    def on_closing(self):
        self.file_manager.saveLibraryData(self.library)
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
