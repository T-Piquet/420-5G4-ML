import os
import sys
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime

# Import the compiled C++ module
try:
    import library_core
except ImportError:
    print("ERROR: library_core module not found. Build the pybind11 module first.")
    sys.exit(1)

# ---------------- Configuration ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

BOOKS_FILE = os.path.join(DATA_DIR, "books.txt")
USERS_FILE = os.path.join(DATA_DIR, "users.txt")


# ---------------- Main App ----------------
class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Système de Gestion de Bibliothèque Personnelle")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Core objects
        self.library = library_core.Library()
        self.file_manager = library_core.FileManager(BOOKS_FILE, USERS_FILE)

        try:
            self.file_manager.loadLibraryData(self.library)
        except Exception as e:
            messagebox.showwarning("Chargement", f"Impossible de charger les données : {e}")

        # Layout: sidebar + content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Show dashboard initially
        self.show_dashboard()

    # ---------- Sidebar ----------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(20, weight=1)

        title = ctk.CTkLabel(
            sidebar, text="📚 Bibliothèque",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(25, 20))

        buttons = [
            ("🏠 Tableau de bord", self.show_dashboard),
            ("➕ Ajouter un livre", self.show_add_book),
            ("➖ Supprimer un livre", self.show_remove_book),
            ("🔍 Rechercher par titre", self.show_search_title),
            ("🔍 Rechercher par auteur", self.show_search_author),
            ("📖 Tous les livres", self.show_all_books),
            ("✅ Livres disponibles", self.show_available_books),
            ("👤 Ajouter un utilisateur", self.show_add_user),
            ("👥 Tous les utilisateurs", self.show_all_users),
            ("📤 Emprunter un livre", self.show_checkout),
            ("📥 Retourner un livre", self.show_return),
            ("📊 Statistiques", self.show_stats),
            ("💾 Sauvegarder", self.action_save),
            ("🗄️ Créer une sauvegarde", self.action_backup),
        ]

        for idx, (text, command) in enumerate(buttons, start=1):
            btn = ctk.CTkButton(
                sidebar, text=text, anchor="w",
                command=command, height=34,
                fg_color="transparent", hover_color=("gray70", "gray30"),
            )
            btn.grid(row=idx, column=0, padx=12, pady=2, sticky="ew")

        # Exit at bottom
        exit_btn = ctk.CTkButton(
            sidebar, text="🚪 Quitter", anchor="w",
            command=self.on_exit, height=36,
            fg_color="#a83232", hover_color="#7d2525"
        )
        exit_btn.grid(row=21, column=0, padx=12, pady=(10, 20), sticky="ew")

    # ---------- Content ----------
    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, corner_radius=10)
        self.content.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _header(self, text, subtitle=""):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header, text=text,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(
                header, text=subtitle,
                font=ctk.CTkFont(size=13), text_color="gray70"
            ).pack(anchor="w", pady=(2, 0))

    def _scrollable_text(self, text, row=1):
        box = ctk.CTkTextbox(self.content, wrap="word", font=ctk.CTkFont(family="Consolas", size=13))
        box.grid(row=row, column=0, padx=20, pady=(5, 15), sticky="nsew")
        self.content.grid_rowconfigure(row, weight=1)
        box.insert("1.0", text)
        box.configure(state="disabled")
        return box

    def _refresh_text(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    # ---------- Book Display Helpers ----------
    def _book_to_str(self, book):
        status = "✅ Disponible" if book.isAvailable else f"❌ Emprunté par {book.borrowerId}"
        return (
            f"📖 Titre   : {book.title}\n"
            f"✍️  Auteur  : {book.author}\n"
            f"🔖 ISBN    : {book.isbn}\n"
            f"📌 Statut  : {status}\n"
            f"{'-' * 55}\n"
        )

    def _user_to_str(self, user):
        return (
            f"👤 Nom     : {user.name}\n"
            f"🆔 ID      : {user.userId}\n"
            f"{'-' * 55}\n"
        )

    # ---------- Views ----------
    def show_dashboard(self):
        self._clear_content()
        self._header("Tableau de bord", "Vue d'ensemble de votre bibliothèque")

        stats_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

        total = self.library.getTotalBooks()
        avail = self.library.getAvailableBookCount()
        out = self.library.getCheckedOutBookCount()
        users = len(self.library.getAllUsers())

        cards = [
            ("📚 Total Livres", total, "#1f6aa5"),
            ("✅ Disponibles", avail, "#2f8c4b"),
            ("📤 Empruntés", out, "#b86b1e"),
            ("👥 Utilisateurs", users, "#6a4ba5"),
        ]
        for i, (label, value, color) in enumerate(cards):
            card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=12, height=110)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=13)).pack(pady=(18, 4))
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=32, weight="bold")).pack()

        # Recent books
        ctk.CTkLabel(
            self.content, text="📖 Aperçu des livres",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")

        books = self.library.getAllBooks()
        if not books:
            text = "Aucun livre dans la bibliothèque.\nAjoutez votre premier livre depuis le menu."
        else:
            text = "".join(self._book_to_str(b) for b in books[:10])
        self._scrollable_text(text, row=3)

    def show_add_book(self):
        self._clear_content()
        self._header("Ajouter un livre", "Remplissez les informations du livre")

        form = ctk.CTkFrame(self.content, fg_color="transparent")
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        entries = {}
        for i, (label, key) in enumerate([("Titre", "title"), ("Auteur", "author"), ("ISBN", "isbn")]):
            ctk.CTkLabel(form, text=f"{label} :").grid(row=i, column=0, padx=(0, 10), pady=8, sticky="w")
            e = ctk.CTkEntry(form, placeholder_text=f"Entrez {label.lower()}...")
            e.grid(row=i, column=1, pady=8, sticky="ew")
            entries[key] = e

        def submit():
            title = entries["title"].get().strip()
            author = entries["author"].get().strip()
            isbn = entries["isbn"].get().strip()

            if not title or not author or not isbn:
                messagebox.showwarning("Champs requis", "Tous les champs sont obligatoires.")
                return

            if self.library.findBookByISBN(isbn):
                messagebox.showerror("Erreur", f"Un livre avec l'ISBN '{isbn}' existe déjà.")
                return

            try:
                book = library_core.Book(title, author, isbn)
                self.library.addBook(book)
                messagebox.showinfo("Succès", f"Livre '{title}' ajouté avec succès !")
                for e in entries.values():
                    e.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        ctk.CTkButton(
            form, text="✅ Ajouter le livre", command=submit,
            height=42, width=200
        ).grid(row=3, column=0, columnspan=2, pady=(20, 0))

    def show_remove_book(self):
        self._clear_content()
        self._header("Supprimer un livre", "Entrez l'ISBN du livre à supprimer")

        form = ctk.CTkFrame(self.content, fg_color="transparent")
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="ISBN :").grid(row=0, column=0, padx=(0, 10), sticky="w")
        isbn_entry = ctk.CTkEntry(form, placeholder_text="Entrez l'ISBN...")
        isbn_entry.grid(row=0, column=1, sticky="ew")

        def submit():
            isbn = isbn_entry.get().strip()
            if not isbn:
                messagebox.showwarning("Champ requis", "Veuillez entrer un ISBN.")
                return
            try:
                if self.library.removeBook(isbn):
                    messagebox.showinfo("Succès", f"Livre avec ISBN '{isbn}' supprimé.")
                    isbn_entry.delete(0, "end")
                else:
                    messagebox.showerror("Erreur", f"Aucun livre trouvé avec l'ISBN '{isbn}'.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        ctk.CTkButton(
            form, text="🗑️ Supprimer", command=submit,
            height=42, width=200, fg_color="#a83232", hover_color="#7d2525"
        ).grid(row=1, column=0, columnspan=2, pady=(20, 0))

    def _search_view(self, title_text, search_fn, field_label):
        self._clear_content()
        self._header(title_text)

        form = ctk.CTkFrame(self.content, fg_color="transparent")
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text=f"{field_label} :").grid(row=0, column=0, padx=(0, 10), sticky="w")
        entry = ctk.CTkEntry(form, placeholder_text=f"Entrez {field_label.lower()}...")
        entry.grid(row=0, column=1, sticky="ew")

        results_box = ctk.CTkTextbox(self.content, wrap="word", font=ctk.CTkFont(family="Consolas", size=13))
        results_box.grid(row=2, column=0, padx=20, pady=15, sticky="nsew")
        self.content.grid_rowconfigure(2, weight=1)
        results_box.insert("1.0", "Entrez une recherche et appuyez sur Rechercher.")
        results_box.configure(state="disabled")

        def submit(_=None):
            query = entry.get().strip()
            if not query:
                messagebox.showwarning("Champ requis", f"Veuillez entrer un {field_label.lower()}.")
                return
            try:
                results = search_fn(query)
                if not results:
                    text = f"Aucun résultat pour '{query}'."
                else:
                    text = f"🔎 {len(results)} résultat(s) pour '{query}' :\n\n"
                    text += "".join(self._book_to_str(b) for b in results)
                self._refresh_text(results_box, text)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        ctk.CTkButton(form, text="🔍 Rechercher", command=submit, height=42, width=200).grid(
            row=1, column=0, columnspan=2, pady=(15, 0)
        )
        entry.bind("<Return>", submit)

    def show_search_title(self):
        self._search_view("Rechercher par titre", self.library.searchBooksByTitle, "Titre")

    def show_search_author(self):
        self._search_view("Rechercher par auteur", self.library.searchBooksByAuthor, "Auteur")

    def show_all_books(self):
        self._clear_content()
        self._header("Tous les livres")
        books = self.library.getAllBooks()
        if not books:
            text = "Aucun livre dans la bibliothèque."
        else:
            text = f"📚 {len(books)} livre(s) :\n\n" + "".join(self._book_to_str(b) for b in books)
        self._scrollable_text(text)

    def show_available_books(self):
        self._clear_content()
        self._header("Livres disponibles")
        books = [b for b in self.library.getAllBooks() if b.isAvailable]
        if not books:
            text = "Aucun livre disponible pour le moment."
        else:
            text = f"✅ {len(books)} livre(s) disponible(s) :\n\n" + "".join(self._book_to_str(b) for b in books)
        self._scrollable_text(text)

    def show_add_user(self):
        self._clear_content()
        self._header("Ajouter un utilisateur", "Remplissez les informations")

        form = ctk.CTkFrame(self.content, fg_color="transparent")
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        entries = {}
        for i, (label, key) in enumerate([("Nom", "name"), ("ID", "userId")]):
            ctk.CTkLabel(form, text=f"{label} :").grid(row=i, column=0, padx=(0, 10), pady=8, sticky="w")
            e = ctk.CTkEntry(form, placeholder_text=f"Entrez {label.lower()}...")
            e.grid(row=i, column=1, pady=8, sticky="ew")
            entries[key] = e

        def submit():
            name = entries["name"].get().strip()
            uid = entries["userId"].get().strip()
            if not name or not uid:
                messagebox.showwarning("Champs requis", "Tous les champs sont obligatoires.")
                return
            if self.library.findUserById(uid):
                messagebox.showerror("Erreur", f"Un utilisateur avec l'ID '{uid}' existe déjà.")
                return
            try:
                user = library_core.User(name, uid)
                self.library.addUser(user)
                messagebox.showinfo("Succès", f"Utilisateur '{name}' ajouté !")
                for e in entries.values():
                    e.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        ctk.CTkButton(
            form, text="✅ Ajouter l'utilisateur", command=submit,
            height=42, width=200
        ).grid(row=2, column=0, columnspan=2, pady=(20, 0))

    def show_all_users(self):
        self._clear_content()
        self._header("Tous les utilisateurs")
        users = self.library.getAllUsers()
        if not users:
            text = "Aucun utilisateur enregistré."
        else:
            text = f"👥 {len(users)} utilisateur(s) :\n\n" + "".join(self._user_to_str(u) for u in users)
        self._scrollable_text(text)

    def _book_action_view(self, title_text, submit_label, action_fn, needs_user=False):
        self._clear_content()
        self._header(title_text)

        form = ctk.CTkFrame(self.content, fg_color="transparent")
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="ISBN :").grid(row=0, column=0, padx=(0, 10), pady=8, sticky="w")
        isbn_entry = ctk.CTkEntry(form, placeholder_text="Entrez l'ISBN...")
        isbn_entry.grid(row=0, column=1, pady=8, sticky="ew")

        user_entry = None
        if needs_user:
            ctk.CTkLabel(form, text="ID Utilisateur :").grid(row=1, column=0, padx=(0, 10), pady=8, sticky="w")
            user_entry = ctk.CTkEntry(form, placeholder_text="Entrez l'ID utilisateur...")
            user_entry.grid(row=1, column=1, pady=8, sticky="ew")

        def submit():
            isbn = isbn_entry.get().strip()
            if not isbn:
                messagebox.showwarning("Champ requis", "Veuillez entrer un ISBN.")
                return
            try:
                if needs_user:
                    uid = user_entry.get().strip()
                    if not uid:
                        messagebox.showwarning("Champ requis", "Veuillez entrer un ID utilisateur.")
                        return
                    ok = action_fn(isbn, uid)
                else:
                    ok = action_fn(isbn)

                if ok:
                    messagebox.showinfo("Succès", submit_label + " effectué avec succès !")
                    isbn_entry.delete(0, "end")
                    if user_entry:
                        user_entry.delete(0, "end")
                else:
                    messagebox.showerror(
                        "Erreur",
                        "Opération échouée. Vérifiez l'ISBN, l'ID utilisateur et la disponibilité."
                    )
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        row = 2 if needs_user else 2
        ctk.CTkButton(form, text=submit_label, command=submit, height=42, width=220).grid(
            row=row, column=0, columnspan=2, pady=(20, 0)
        )

    def show_checkout(self):
        self._book_action_view(
            "Emprunter un livre", "📤 Emprunter", self.library.checkOutBook, needs_user=True
        )

    def show_return(self):
        self._book_action_view(
            "Retourner un livre", "📥 Retourner", self.library.returnBook, needs_user=False
        )

    def show_stats(self):
        self._clear_content()
        self._header("Statistiques de la bibliothèque")

        stats_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

        total = self.library.getTotalBooks()
        avail = self.library.getAvailableBookCount()
        out = self.library.getCheckedOutBookCount()
        users = len(self.library.getAllUsers())

        cards = [
            ("📚 Total Livres", total, "#1f6aa5"),
            ("✅ Disponibles", avail, "#2f8c4b"),
            ("📤 Empruntés", out, "#b86b1e"),
            ("👥 Utilisateurs", users, "#6a4ba5"),
        ]
        for i, (label, value, color) in enumerate(cards):
            card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=12, height=140)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=14)).pack(pady=(25, 8))
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=40, weight="bold")).pack()

    def action_save(self):
        try:
            if self.file_manager.saveLibraryData(self.library):
                messagebox.showinfo("Sauvegarde", "Données sauvegardées avec succès !")
            else:
                messagebox.showerror("Erreur", "Échec de la sauvegarde.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def action_backup(self):
        try:
            self.file_manager.createBackup()
            messagebox.showinfo("Sauvegarde", "Sauvegarde créée avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def on_exit(self):
        try:
            self.file_manager.saveLibraryData(self.library)
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()