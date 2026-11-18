import sys
from pathlib import Path
from tkinter import ttk

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

        if not self.gestionnaire.loadLibraryData(self.bibliotheque):
            print("Erreur : chargement des données impossible.")

        tabview = customtkinter.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        onglet_livres = tabview.add("Livres")
        tabview.add("Utilisateurs")
        tabview.add("Emprunts")
        tabview.add("Statistiques")

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

        self.rafraichir_livres()

    def rafraichir_livres(self):
        for item in self.tree_livres.get_children():
            self.tree_livres.delete(item)

        for livre in self.bibliotheque.getAllBooks():
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
