
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import bibliotheque_cpp as cpp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Application(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Gestion de bibliothèque")
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Initialisation de la bibliothèque C++
        dossier = Path(__file__).resolve().parent / "data"

        self.library = cpp.Library()
        self.manager = cpp.FileManager(
            str(dossier / "books.txt"),
            str(dossier / "users.txt")
        )

        self.chargement_ok = self.manager.loadLibraryData(self.library)

        # Configuration de la fenêtre
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="BIBLIOTHÈQUE",
            font=("Arial", 20, "bold")
        ).grid(row=0, column=0, padx=15, pady=30)

        ecrans = [
            ("Accueil", self.accueil),
            ("Livres", self.livres),
            ("Utilisateurs", self.utilisateurs),
            ("Emprunts", self.emprunts),
            ("Sauvegardes", self.sauvegardes)
        ]

        for i, (nom, commande) in enumerate(ecrans, start=1):
            ctk.CTkButton(
                self.sidebar,
                text=nom,
                command=commande,
                height=45
            ).grid(row=i, column=0, padx=15, pady=8, sticky="ew")

        ctk.CTkButton(
            self.sidebar,
            text="Quitter",
            fg_color="#a83232",
            hover_color="#802626",
            command=self.quitter
        ).grid(row=7, column=0, padx=15, pady=20, sticky="ew")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(
            row=0, column=1, padx=25, pady=25, sticky="nsew"
        )

        self.protocol("WM_DELETE_WINDOW", self.quitter)

        self.accueil()

        if not self.chargement_ok:
            messagebox.showerror(
                "Erreur",
                "Impossible de charger toutes les données. "
                "La sauvegarde est désactivée par sécurité."
            )

    # Utilitaires graphiques

    def preparer_ecran(self, titre):
        for widget in self.content.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.content,
            text=titre,
            font=("Arial", 30, "bold")
        ).pack(anchor="w", pady=(0, 20))

    def champ(self, parent, texte):
        ctk.CTkLabel(parent, text=texte).pack(
            anchor="w", padx=10, pady=(8, 0)
        )

        entree = ctk.CTkEntry(parent, placeholder_text=texte)
        entree.pack(fill="x", padx=10, pady=5)
        return entree

    def bouton(self, parent, texte, commande):
        ctk.CTkButton(
            parent, text=texte, command=commande
        ).pack(fill="x", padx=10, pady=6)

    def message(self, texte):
        messagebox.showinfo("Bibliothèque", texte)

    def erreur(self, texte):
        messagebox.showerror("Erreur", texte)

    def tableau(self, parent, colonnes, lignes):
        for widget in parent.winfo_children():
            widget.destroy()

        for i in range(len(colonnes)):
            parent.grid_columnconfigure(i, weight=1)

        for i, colonne in enumerate(colonnes):
            ctk.CTkLabel(
                parent,
                text=colonne,
                font=("Arial", 13, "bold"),
                fg_color="#24466b",
                corner_radius=4
            ).grid(row=0, column=i, padx=2, pady=4, sticky="ew")

        for numero, ligne in enumerate(lignes, start=1):
            couleur = "#292929" if numero % 2 else "#333333"

            for i, valeur in enumerate(ligne):
                ctk.CTkLabel(
                    parent,
                    text=str(valeur),
                    fg_color=couleur,
                    wraplength=230
                ).grid(
                    row=numero, column=i,
                    padx=2, pady=2, sticky="nsew"
                )

    # Écran Accueil

    def accueil(self):
        self.preparer_ecran("Tableau de bord")

        ctk.CTkLabel(
            self.content,
            text="Vue d'ensemble de votre bibliothèque",
            font=("Arial", 16)
        ).pack(anchor="w", pady=(0, 20))

        grille = ctk.CTkFrame(self.content, fg_color="transparent")
        grille.pack(fill="both", expand=True)

        statistiques = [
            ("Total des livres", self.library.getTotalBooks()),
            ("Livres disponibles", self.library.getAvailableBookCount()),
            ("Livres empruntés", self.library.getCheckedOutBookCount()),
            ("Utilisateurs", len(self.library.getAllUsers()))
        ]

        grille.grid_columnconfigure((0, 1), weight=1)
        grille.grid_rowconfigure((0, 1), weight=1)

        for i, (titre, valeur) in enumerate(statistiques):
            carte = ctk.CTkFrame(grille, corner_radius=12)
            carte.grid(
                row=i // 2, column=i % 2,
                padx=10, pady=10, sticky="nsew"
            )

            ctk.CTkLabel(
                carte,
                text=titre,
                font=("Arial", 18)
            ).pack(pady=(30, 10))

            ctk.CTkLabel(
                carte,
                text=str(valeur),
                font=("Arial", 48, "bold"),
                text_color="#5599ee"
            ).pack(pady=10)

    # Écran Livres

    def livres(self):
        self.preparer_ecran("Gestion des livres")

        recherche = ctk.CTkFrame(self.content)
        recherche.pack(fill="x", pady=(0, 10))

        texte = ctk.CTkEntry(
            recherche, placeholder_text="Rechercher un livre..."
        )
        texte.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        mode = ctk.CTkOptionMenu(
            recherche, values=["Titre", "Auteur"]
        )
        mode.pack(side="left", padx=5)

        zone = ctk.CTkFrame(self.content, fg_color="transparent")
        zone.pack(fill="both", expand=True)

        formulaire = ctk.CTkFrame(zone, width=240)
        formulaire.pack(side="left", fill="y", padx=(0, 10))

        liste = ctk.CTkScrollableFrame(zone)
        liste.pack(side="right", fill="both", expand=True)

        def afficher(livres):
            lignes = [
                (
                    livre.getTitle(),
                    livre.getAuthor(),
                    livre.getISBN(),
                    "Disponible" if livre.getAvailability()
                    else "Emprunté"
                )
                for livre in livres
            ]

            self.tableau(
                liste,
                ["Titre", "Auteur", "ISBN", "Statut"],
                lignes
            )

        def chercher():
            valeur = texte.get().strip()

            if mode.get() == "Titre":
                afficher(self.library.searchBooksByTitle(valeur))
            else:
                afficher(self.library.searchBooksByAuthor(valeur))

        ctk.CTkButton(
            recherche, text="Rechercher", command=chercher
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            recherche,
            text="Tous",
            width=65,
            command=lambda: afficher(self.library.getAllBooks())
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            formulaire, text="Ajouter un livre",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        titre = self.champ(formulaire, "Titre")
        auteur = self.champ(formulaire, "Auteur")
        isbn = self.champ(formulaire, "ISBN")

        def ajouter():
            valeurs = [e.get().strip() for e in (titre, auteur, isbn)]

            if not all(valeurs):
                return self.erreur("Tous les champs sont obligatoires.")

            if self.library.findBookByISBN(valeurs[2]) is not None:
                return self.erreur("Cet ISBN existe déjà.")

            self.library.addBook(cpp.Book(*valeurs))

            for entree in (titre, auteur, isbn):
                entree.delete(0, "end")

            afficher(self.library.getAllBooks())
            self.message("Livre ajouté.")

        self.bouton(formulaire, "Ajouter", ajouter)

        ctk.CTkLabel(
            formulaire,
            text="Supprimer un livre",
            font=("Arial", 18, "bold")
        ).pack(pady=(25, 5))

        isbn_supprimer = self.champ(formulaire, "ISBN à supprimer")

        def supprimer():
            valeur = isbn_supprimer.get().strip()

            if not valeur:
                return self.erreur("Saisissez un ISBN.")

            if not messagebox.askyesno(
                "Confirmation", "Supprimer ce livre ?"
            ):
                return

            if self.library.removeBook(valeur):
                afficher(self.library.getAllBooks())
                isbn_supprimer.delete(0, "end")
                self.message("Livre supprimé.")
            else:
                self.erreur("Impossible de supprimer ce livre.")

        self.bouton(formulaire, "Supprimer", supprimer)

        self.bouton(
            formulaire,
            "Livres disponibles",
            lambda: afficher(self.library.getAvailableBooks())
        )

        afficher(self.library.getAllBooks())

    # Écran Utilisateurs

    def utilisateurs(self):
        self.preparer_ecran("Gestion des utilisateurs")

        formulaire = ctk.CTkFrame(self.content)
        formulaire.pack(fill="x", pady=(0, 15))

        nom = self.champ(formulaire, "Nom")
        identifiant = self.champ(formulaire, "Identifiant utilisateur")

        liste = ctk.CTkScrollableFrame(self.content)
        liste.pack(fill="both", expand=True)

        def afficher():
            lignes = [
                (
                    utilisateur.getName(),
                    utilisateur.getUserId(),
                    utilisateur.getNumberOfBorrowedBooks(),
                    ", ".join(utilisateur.getBorrowedBooks()) or "Aucun"
                )
                for utilisateur in self.library.getAllUsers()
            ]

            self.tableau(
                liste,
                ["Nom", "Identifiant", "Nombre d'emprunts", "ISBN empruntés"],
                lignes
            )

        def ajouter():
            n = nom.get().strip()
            i = identifiant.get().strip()

            if not n or not i:
                return self.erreur("Tous les champs sont obligatoires.")

            if self.library.findUserById(i) is not None:
                return self.erreur("Cet identifiant existe déjà.")

            self.library.addUser(cpp.User(n, i))

            nom.delete(0, "end")
            identifiant.delete(0, "end")

            afficher()
            self.message("Utilisateur ajouté.")

        self.bouton(formulaire, "Ajouter un utilisateur", ajouter)

        afficher()

    # Écran Emprunts

    def emprunts(self):
        self.preparer_ecran("Gestion des emprunts")

        formulaires = ctk.CTkFrame(self.content, fg_color="transparent")
        formulaires.pack(fill="x", pady=(0, 15))

        formulaires.grid_columnconfigure((0, 1), weight=1)

        emprunt = ctk.CTkFrame(formulaires)
        emprunt.grid(row=0, column=0, padx=5, sticky="nsew")

        retour = ctk.CTkFrame(formulaires)
        retour.grid(row=0, column=1, padx=5, sticky="nsew")

        ctk.CTkLabel(
            emprunt, text="Emprunter un livre",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        isbn = self.champ(emprunt, "ISBN")
        utilisateur = self.champ(emprunt, "Identifiant utilisateur")

        ctk.CTkLabel(
            retour, text="Retourner un livre",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        isbn_retour = self.champ(retour, "ISBN")

        ctk.CTkLabel(
            self.content,
            text="Livres actuellement empruntés",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", pady=10)

        liste = ctk.CTkScrollableFrame(self.content)
        liste.pack(fill="both", expand=True)

        def afficher():
            lignes = [
                (
                    livre.getTitle(),
                    livre.getISBN(),
                    livre.getBorrowerId()
                )
                for livre in self.library.getAllBooks()
                if not livre.getAvailability()
            ]

            self.tableau(
                liste,
                ["Titre", "ISBN", "Emprunteur"],
                lignes
            )

        def emprunter():
            i = isbn.get().strip()
            u = utilisateur.get().strip()

            if not i or not u:
                return self.erreur("Remplissez tous les champs.")

            if self.library.checkOutBook(i, u):
                afficher()
                isbn.delete(0, "end")
                utilisateur.delete(0, "end")
                self.message("Emprunt enregistré.")
            else:
                self.erreur("Emprunt impossible.")

        def retourner():
            i = isbn_retour.get().strip()

            if not i:
                return self.erreur("Saisissez un ISBN.")

            if self.library.returnBook(i):
                afficher()
                isbn_retour.delete(0, "end")
                self.message("Livre retourné.")
            else:
                self.erreur("Retour impossible.")

        self.bouton(emprunt, "Emprunter", emprunter)
        self.bouton(retour, "Retourner", retourner)

        afficher()

    # Écran Sauvegardes

    def sauvegardes(self):
        self.preparer_ecran("Sauvegardes")

        carte = ctk.CTkFrame(self.content)
        carte.pack(fill="x", pady=10)

        ctk.CTkLabel(
            carte,
            text="Enregistrement des données",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            carte,
            text="Les données sont enregistrées dans books.txt et users.txt."
        ).pack(pady=10)

        self.bouton(carte, "Sauvegarder les données", self.sauvegarder)
        self.bouton(carte, "Créer une sauvegarde", self.creer_backup)

    def sauvegarder(self):
        if not self.chargement_ok:
            self.erreur("Sauvegarde désactivée : chargement incomplet.")
            return False

        if self.manager.saveLibraryData(self.library):
            self.message("Données sauvegardées.")
            return True

        self.erreur("Échec de la sauvegarde.")
        return False

    def creer_backup(self):
        if not self.chargement_ok:
            return self.erreur("Chargement des données incomplet.")

        if self.manager.saveLibraryData(self.library):
            self.manager.createBackup()
            self.message(
                "Création de la sauvegarde demandée. "
                "Vérifiez les fichiers générés."
            )
        else:
            self.erreur("Impossible d'enregistrer les données.")

    # Fermeture de l'application

    def quitter(self):
        if not messagebox.askyesno(
            "Quitter", "Voulez-vous fermer l'application ?"
        ):
            return

        if self.chargement_ok:
            if self.manager.saveLibraryData(self.library):
                self.destroy()
            else:
                self.erreur("Échec de la sauvegarde.")
        else:
            if messagebox.askyesno(
                "Attention", "Quitter sans sauvegarder ?"
            ):
                self.destroy()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
