import sys
from pathlib import Path
from tkinter import ttk, messagebox
sys.path.insert(0, str(Path(__file__).resolve().parent))

import customtkinter
import biblio


DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "data"


class Application(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bibliothèque")
        self.geometry("900x600")

        self.bibliotheque = biblio.Library()
        self.gestionnaire = biblio.FileManager(
            str(DOSSIER_DONNEES / "books.txt"),
            str(DOSSIER_DONNEES / "users.txt"),
        )
        self.journal = biblio.ActivityLogger(str(DOSSIER_DONNEES / "journal.log"))

        if not self.gestionnaire.loadLibraryData(self.bibliotheque):
            print("Erreur : chargement des données impossible.")

        tabview = customtkinter.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        cadre_fichier = customtkinter.CTkFrame(self)
        cadre_fichier.pack(fill="x", padx=10, pady=5)

        bouton_sauvegarder = customtkinter.CTkButton(
            cadre_fichier, text="Sauvegarder", command=self.sauvegarder_donnees
        )
        bouton_sauvegarder.pack(side="left", padx=5, pady=5)

        bouton_backup = customtkinter.CTkButton(
            cadre_fichier, text="Créer une sauvegarde", command=self.creer_sauvegarde
        )
        bouton_backup.pack(side="left", padx=5, pady=5)

        bouton_quitter = customtkinter.CTkButton(
            cadre_fichier, text="Quitter", command=self.quitter_application
        )
        bouton_quitter.pack(side="left", padx=5, pady=5)

        onglet_livres = tabview.add("Livres")
        onglet_utilisateurs = tabview.add("Utilisateurs")
        onglet_emprunts = tabview.add("Emprunts")
        onglet_statistiques = tabview.add("Statistiques")

        barre_livres = customtkinter.CTkFrame(onglet_livres)
        barre_livres.pack(fill="x", padx=5, pady=5)

        self.entree_recherche_livre = customtkinter.CTkEntry(
            barre_livres, placeholder_text="Recherche..."
        )
        self.entree_recherche_livre.pack(side="left", padx=5, pady=5)

        self.option_recherche_livre = customtkinter.CTkOptionMenu(
            barre_livres, values=["Titre", "Auteur"]
        )
        self.option_recherche_livre.set("Titre")
        self.option_recherche_livre.pack(side="left", padx=5, pady=5)

        self.case_disponibles_seulement = customtkinter.CTkCheckBox(
            barre_livres, text="Disponibles seulement"
        )
        self.case_disponibles_seulement.pack(side="left", padx=5, pady=5)

        self.option_tri_livre = customtkinter.CTkOptionMenu(
            barre_livres, values=["Titre", "Auteur"]
        )
        self.option_tri_livre.set("Titre")
        self.option_tri_livre.pack(side="left", padx=5, pady=5)

        colonnes = ("titre", "auteur", "isbn", "disponible")
        self.tree_livres = ttk.Treeview(
            onglet_livres,
            columns=colonnes,
            show="headings",
        )
        self.tree_livres.heading("titre", text="Titre")
        self.tree_livres.heading("auteur", text="Auteur")
        self.tree_livres.heading("isbn", text="ISBN")
        self.tree_livres.heading("disponible", text="Disponible")

        self.tree_livres.column("titre", width=300)
        self.tree_livres.column("auteur", width=220)
        self.tree_livres.column("isbn", width=180)
        self.tree_livres.column("disponible", width=120)

        self.tree_livres.pack(fill="both", expand=True, padx=5, pady=5)

        self.entree_recherche_livre.bind("<KeyRelease>", lambda e: self.rafraichir_livres())
        self.option_recherche_livre.configure(command=lambda _: self.rafraichir_livres())
        self.case_disponibles_seulement.configure(command=self.rafraichir_livres)
        self.option_tri_livre.configure(command=lambda _: self.rafraichir_livres())

        cadre_ajout_livre = customtkinter.CTkFrame(onglet_livres)
        cadre_ajout_livre.pack(fill="x", padx=5, pady=5)

        self.entree_titre_livre = customtkinter.CTkEntry(
            cadre_ajout_livre, placeholder_text="Titre"
        )
        self.entree_titre_livre.pack(side="left", padx=5, pady=5)

        self.entree_auteur_livre = customtkinter.CTkEntry(
            cadre_ajout_livre, placeholder_text="Auteur"
        )
        self.entree_auteur_livre.pack(side="left", padx=5, pady=5)

        self.entree_isbn_livre = customtkinter.CTkEntry(
            cadre_ajout_livre, placeholder_text="ISBN"
        )
        self.entree_isbn_livre.pack(side="left", padx=5, pady=5)

        bouton_ajouter_livre = customtkinter.CTkButton(
            cadre_ajout_livre, text="Ajouter", command=self.ajouter_livre
        )
        bouton_ajouter_livre.pack(side="left", padx=5, pady=5)

        bouton_supprimer_livre = customtkinter.CTkButton(
            cadre_ajout_livre, text="Supprimer", command=self.supprimer_livre
        )
        bouton_supprimer_livre.pack(side="left", padx=5, pady=5)

        colonnes_utilisateurs = ("id", "nom", "nb_emprunts")
        self.tree_utilisateurs = ttk.Treeview(
            onglet_utilisateurs,
            columns=colonnes_utilisateurs,
            show="headings",
        )
        self.tree_utilisateurs.heading("id", text="ID")
        self.tree_utilisateurs.heading("nom", text="Nom")
        self.tree_utilisateurs.heading("nb_emprunts", text="Livres empruntés")
        self.tree_utilisateurs.column("id", width=120)
        self.tree_utilisateurs.column("nom", width=300)
        self.tree_utilisateurs.column("nb_emprunts", width=180)
        self.tree_utilisateurs.pack(fill="both", expand=True, padx=5, pady=5)

        cadre_ajout_utilisateur = customtkinter.CTkFrame(onglet_utilisateurs)
        cadre_ajout_utilisateur.pack(fill="x", padx=5, pady=5)

        self.entree_nom_utilisateur = customtkinter.CTkEntry(
            cadre_ajout_utilisateur, placeholder_text="Nom"
        )
        self.entree_nom_utilisateur.pack(side="left", padx=5, pady=5)

        bouton_ajouter_utilisateur = customtkinter.CTkButton(
            cadre_ajout_utilisateur,
            text="Ajouter un utilisateur",
            command=self.ajouter_utilisateur,
        )
        bouton_ajouter_utilisateur.pack(side="left", padx=5, pady=5)

        cadre_emprunt = customtkinter.CTkFrame(onglet_emprunts)
        cadre_emprunt.pack(fill="x", padx=5, pady=5)

        self.option_livre_disponible = customtkinter.CTkOptionMenu(cadre_emprunt, values=[""])
        self.option_livre_disponible.set("")
        self.option_livre_disponible.pack(side="left", padx=5, pady=5)

        self.option_utilisateur_emprunt = customtkinter.CTkOptionMenu(cadre_emprunt, values=[""])
        self.option_utilisateur_emprunt.set("")
        self.option_utilisateur_emprunt.pack(side="left", padx=5, pady=5)

        bouton_emprunter = customtkinter.CTkButton(
            cadre_emprunt, text="Emprunter", command=self.emprunter_livre
        )
        bouton_emprunter.pack(side="left", padx=5, pady=5)

        cadre_retour = customtkinter.CTkFrame(onglet_emprunts)
        cadre_retour.pack(fill="x", padx=5, pady=5)

        self.option_livre_emprunte = customtkinter.CTkOptionMenu(cadre_retour, values=[""])
        self.option_livre_emprunte.set("")
        self.option_livre_emprunte.pack(side="left", padx=5, pady=5)

        bouton_retourner = customtkinter.CTkButton(
            cadre_retour, text="Retourner", command=self.retourner_livre
        )
        bouton_retourner.pack(side="left", padx=5, pady=5)

        self.label_stats_total = customtkinter.CTkLabel(onglet_statistiques, text="Total des livres : 0")
        self.label_stats_total.pack(anchor="w", padx=10, pady=5)
        self.label_stats_disponibles = customtkinter.CTkLabel(onglet_statistiques, text="Disponibles : 0")
        self.label_stats_disponibles.pack(anchor="w", padx=10, pady=5)
        self.label_stats_empruntes = customtkinter.CTkLabel(onglet_statistiques, text="Empruntés : 0")
        self.label_stats_empruntes.pack(anchor="w", padx=10, pady=5)
        self.label_stats_utilisateurs = customtkinter.CTkLabel(onglet_statistiques, text="Utilisateurs : 0")
        self.label_stats_utilisateurs.pack(anchor="w", padx=10, pady=5)

        self.rafraichir_livres()
        self.rafraichir_utilisateurs()
        self.rafraichir_emprunts()
        self.rafraichir_statistiques()

        self.protocol("WM_DELETE_WINDOW", self.quitter_application)

    def rafraichir_statistiques(self):
        total = self.bibliotheque.getTotalBooks()
        disponibles = self.bibliotheque.getAvailableBookCount()
        empruntes = self.bibliotheque.getCheckedOutBookCount()
        utilisateurs = len(self.bibliotheque.getAllUsers())
        self.label_stats_total.configure(text=f"Total des livres : {total}")
        self.label_stats_disponibles.configure(text=f"Disponibles : {disponibles}")
        self.label_stats_empruntes.configure(text=f"Empruntés : {empruntes}")
        self.label_stats_utilisateurs.configure(text=f"Utilisateurs : {utilisateurs}")

    def rafraichir_emprunts(self):
        livres_disponibles = self.bibliotheque.getAvailableBooks()
        valeurs_livres_disponibles = []
        for livre in livres_disponibles:
            valeurs_livres_disponibles.append(f"{livre.getISBN()} - {livre.getTitle()}")
        if len(valeurs_livres_disponibles) == 0:
            valeurs_livres_disponibles = [""]
        self.option_livre_disponible.configure(values=valeurs_livres_disponibles)
        self.option_livre_disponible.set(valeurs_livres_disponibles[0])

        utilisateurs = sorted(self.bibliotheque.getAllUsers(), key=lambda u: u.getUserId())
        valeurs_utilisateurs = []
        for utilisateur in utilisateurs:
            valeurs_utilisateurs.append(f"{utilisateur.getUserId()} - {utilisateur.getName()}")
        if len(valeurs_utilisateurs) == 0:
            valeurs_utilisateurs = [""]
        self.option_utilisateur_emprunt.configure(values=valeurs_utilisateurs)
        self.option_utilisateur_emprunt.set(valeurs_utilisateurs[0])

        livres_empruntes = []
        for livre in self.bibliotheque.getAllBooks():
            if not livre.getAvailability():
                livres_empruntes.append(f"{livre.getISBN()} - {livre.getTitle()}")
        if len(livres_empruntes) == 0:
            livres_empruntes = [""]
        self.option_livre_emprunte.configure(values=livres_empruntes)
        self.option_livre_emprunte.set(livres_empruntes[0])

    def emprunter_livre(self):
        livre_choisi = self.option_livre_disponible.get()
        utilisateur_choisi = self.option_utilisateur_emprunt.get()
        if livre_choisi == "" or utilisateur_choisi == "":
            messagebox.showerror("Erreur", "Veuillez choisir un livre disponible et un utilisateur.")
            return
        isbn = livre_choisi.split(" - ", 1)[0]
        identifiant = utilisateur_choisi.split(" - ", 1)[0]
        if not self.bibliotheque.checkOutBook(isbn, identifiant):
            messagebox.showerror("Erreur", "Emprunt impossible.")
            return
        livre = self.bibliotheque.findBookByISBN(isbn)
        utilisateur = self.bibliotheque.findUserById(identifiant)
        nom_utilisateur = ""
        if utilisateur is not None:
            nom_utilisateur = utilisateur.getName()
        if livre is not None:
            self.journal.logBook("EMPRUNT", livre, nom_utilisateur)
        self.rafraichir_emprunts()
        self.rafraichir_livres()
        self.rafraichir_utilisateurs()
        self.rafraichir_statistiques()

    def retourner_livre(self):
        livre_choisi = self.option_livre_emprunte.get()
        if livre_choisi == "":
            messagebox.showerror("Erreur", "Veuillez choisir un livre emprunté.")
            return
        isbn = livre_choisi.split(" - ", 1)[0]
        livre = self.bibliotheque.findBookByISBN(isbn)
        if livre is None:
            messagebox.showerror("Erreur", "Livre introuvable.")
            return
        nom_utilisateur = ""
        utilisateur = self.bibliotheque.findUserById(livre.getBorrowerId())
        if utilisateur is not None:
            nom_utilisateur = utilisateur.getName()
        if not self.bibliotheque.returnBook(isbn):
            messagebox.showerror("Erreur", "Retour impossible.")
            return
        self.journal.logBook("RETOUR", livre, nom_utilisateur)
        self.rafraichir_emprunts()
        self.rafraichir_livres()
        self.rafraichir_utilisateurs()
        self.rafraichir_statistiques()

    def ajouter_livre(self):
        titre = self.entree_titre_livre.get().strip()
        auteur = self.entree_auteur_livre.get().strip()
        isbn = self.entree_isbn_livre.get().strip()

        if titre == "" or auteur == "" or isbn == "":
            messagebox.showerror("Erreur", "Tous les champs (Titre, Auteur, ISBN) sont obligatoires.")
            return

        if self.bibliotheque.findBookByISBN(isbn) is not None:
            messagebox.showerror("Erreur", "Un livre avec cet ISBN existe déjà.")
            return

        livre = biblio.Book(titre, auteur, isbn)
        self.bibliotheque.addBook(livre)
        self.journal.logBook("AJOUT LIVRE", livre)
        self.entree_titre_livre.delete(0, "end")
        self.entree_auteur_livre.delete(0, "end")
        self.entree_isbn_livre.delete(0, "end")
        self.rafraichir_livres()
        self.rafraichir_emprunts()
        self.rafraichir_statistiques()

    def supprimer_livre(self):
        selection = self.tree_livres.selection()
        if len(selection) == 0:
            messagebox.showerror("Erreur", "Aucun livre sélectionné.")
            return

        item = selection[0]
        valeurs = self.tree_livres.item(item, "values")
        isbn = valeurs[2]
        livre = self.bibliotheque.findBookByISBN(isbn)
        if livre is None:
            messagebox.showerror("Erreur", "Livre introuvable.")
            return

        if not livre.getAvailability():
            messagebox.showerror("Erreur", "Impossible de supprimer un livre emprunté.")
            return

        if not messagebox.askyesno("Confirmation", "Supprimer ce livre ?"):
            return

        self.journal.logBook("SUPPRESSION LIVRE", livre)
        self.bibliotheque.removeBook(isbn)
        self.rafraichir_livres()
        self.rafraichir_emprunts()
        self.rafraichir_statistiques()

    def ajouter_utilisateur(self):
        nom = self.entree_nom_utilisateur.get().strip()
        if nom == "":
            messagebox.showerror("Erreur", "Le nom est obligatoire.")
            return

        identifiant = self.bibliotheque.generateUserId()
        utilisateur = biblio.User(nom, identifiant)
        self.bibliotheque.addUser(utilisateur)
        self.journal.log("AJOUT UTILISATEUR", f"{identifiant} - {nom}")
        messagebox.showinfo("Utilisateur ajouté", f"ID créé : {identifiant}")
        self.entree_nom_utilisateur.delete(0, "end")
        self.rafraichir_utilisateurs()
        self.rafraichir_emprunts()
        self.rafraichir_statistiques()

    def rafraichir_utilisateurs(self):
        for item in self.tree_utilisateurs.get_children():
            self.tree_utilisateurs.delete(item)

        utilisateurs = sorted(self.bibliotheque.getAllUsers(), key=lambda u: u.getUserId())
        for utilisateur in utilisateurs:
            self.tree_utilisateurs.insert(
                "",
                "end",
                values=(
                    utilisateur.getUserId(),
                    utilisateur.getName(),
                    utilisateur.getNumberOfBorrowedBooks(),
                ),
            )

    def rafraichir_livres(self):
        for item in self.tree_livres.get_children():
            self.tree_livres.delete(item)

        texte_recherche = self.entree_recherche_livre.get().strip()
        if texte_recherche == "":
            livres = self.bibliotheque.getAllBooks()
        else:
            if self.option_recherche_livre.get() == "Auteur":
                livres = self.bibliotheque.searchBooksByAuthor(texte_recherche)
            else:
                livres = self.bibliotheque.searchBooksByTitle(texte_recherche)

        if self.case_disponibles_seulement.get() == 1:
            livres = [livre for livre in livres if livre.getAvailability()]

        cle_tri = self.option_tri_livre.get()
        if cle_tri == "Auteur":
            livres = sorted(livres, key=lambda livre: livre.getAuthor().lower())
        else:
            livres = sorted(livres, key=lambda livre: livre.getTitle().lower())

        for livre in livres:
            disponible = "Oui" if livre.getAvailability() else "Non"
            self.tree_livres.insert(
                "",
                "end",
                values=(
                    livre.getTitle(),
                    livre.getAuthor(),
                    livre.getISBN(),
                    disponible,
                ),
            )


    def sauvegarder_donnees(self):
        if not self.gestionnaire.saveLibraryData(self.bibliotheque):
            messagebox.showerror("Erreur", "Échec de la sauvegarde.")
            return
        self.journal.log("SAUVEGARDE", "Données sauvegardées")
        messagebox.showinfo("Sauvegarde", "Données sauvegardées.")

    def creer_sauvegarde(self):
        try:
            self.gestionnaire.createBackup()
        except RuntimeError:
            messagebox.showerror("Erreur", "Une sauvegarde existe déjà.")
            return
        self.journal.log("BACKUP", "Sauvegarde créée")
        messagebox.showinfo("Sauvegarde", "Sauvegarde créée.")

    def quitter_application(self):
        if self.gestionnaire.saveLibraryData(self.bibliotheque):
            self.journal.log("QUITTER", "Fermeture de l'application")
        self.destroy()


def main():
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = Application()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
