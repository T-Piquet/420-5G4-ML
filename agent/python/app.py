import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import customtkinter
import biblio


DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "data"


def main():
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    app = customtkinter.CTk()
    app.title("Bibliothèque")
    app.geometry("900x600")

    bibliotheque = biblio.Library()
    gestionnaire = biblio.FileManager(
        str(DOSSIER_DONNEES / "books.txt"),
        str(DOSSIER_DONNEES / "users.txt"),
    )

    if not gestionnaire.loadLibraryData(bibliotheque):
        print("Erreur : chargement des données impossible.")
        return 1

    tabview = customtkinter.CTkTabview(app)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tabview.add("Livres")
    tabview.add("Utilisateurs")
    tabview.add("Emprunts")
    tabview.add("Statistiques")

    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
