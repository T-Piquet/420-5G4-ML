import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import biblio

DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "data"
ISBN_TEST = "9782070612758"
ID_UTILISATEUR = "USR015"


def main():
    bibliotheque = biblio.Library()
    gestionnaire = biblio.FileManager(
        str(DOSSIER_DONNEES / "books.txt"),
        str(DOSSIER_DONNEES / "users.txt"),
    )
    journal = biblio.ActivityLogger(str(DOSSIER_DONNEES / "journal.log"))

    if not gestionnaire.loadLibraryData(bibliotheque):
        print("Erreur : chargement des données impossible.")
        return 1

    print(f"Nombre de livres : {bibliotheque.getTotalBooks()}")

    livre = bibliotheque.findBookByISBN(ISBN_TEST)
    if livre is None:
        print(f"Erreur : livre introuvable pour l'ISBN {ISBN_TEST}.")
        return 1

    print(f"Livre trouvé : {livre.getTitle()} — {livre.getAuthor()}")
    print(f"Disponible avant emprunt : {livre.getAvailability()}")

    if not bibliotheque.checkOutBook(ISBN_TEST, ID_UTILISATEUR):
        print("Erreur : emprunt impossible.")
        return 1
    print(f"Emprunt réussi : emprunteur {livre.getBorrowerId()}")

    if not bibliotheque.returnBook(ISBN_TEST):
        print("Erreur : retour impossible.")
        return 1
    print(f"Retour réussi : disponible = {livre.getAvailability()}")

    journal.log("TEST BIBLIO", f"Emprunt et retour de {ISBN_TEST}")
    print("Ligne écrite dans data/journal.log.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
