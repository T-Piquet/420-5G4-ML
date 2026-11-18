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

        onglet_livres = tabview.add("Livres")
        tabview.add("Utilisateurs")
        tabview.add("Emprunts")
        tabview.add("Statistiques")

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

        self.rafraichir_livres()

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


def main():
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = Application()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
