from pathlib import Path

import bibliotheque_py as bp


class ControleurBibliotheque:
    def __init__(self, repertoire_donnees: str | Path):
        chemin = Path(repertoire_donnees)
        if not chemin.is_dir():
            raise FileNotFoundError(f"Le répertoire de données n'existe pas : {chemin}")

        self.repertoire_donnees = chemin
        self.fichier_livres = chemin / "books.txt"
        self.fichier_utilisateurs = chemin / "users.txt"
        self.bibliotheque = bp.Library()
        self.gestionnaire = bp.FileManager(
            str(self.fichier_livres),
            str(self.fichier_utilisateurs),
        )
        self.gestionnaire.load_library_data(self.bibliotheque)

    @staticmethod
    def _contient_separateur(valeurs: list[str]) -> bool:
        return any("|" in v for v in valeurs)

    def obtenir_statistiques(self) -> dict[str, int]:
        return {
            "total_livres": self.bibliotheque.get_total_books(),
            "disponibles": self.bibliotheque.get_available_book_count(),
            "empruntes": self.bibliotheque.get_checked_out_book_count(),
            "total_utilisateurs": len(self.bibliotheque.get_all_users()),
        }

    def obtenir_tous_les_livres(self):
        return self.bibliotheque.get_all_books()

    def obtenir_livres_disponibles(self):
        return self.bibliotheque.get_available_books()

    def obtenir_livres_empruntes(self):
        return [livre for livre in self.bibliotheque.get_all_books() if not livre.is_available()]

    def rechercher_livres_par_titre(self, titre: str):
        return self.bibliotheque.search_books_by_title(titre.strip())

    def rechercher_livres_par_auteur(self, auteur: str):
        return self.bibliotheque.search_books_by_author(auteur.strip())

    def ajouter_livre(self, titre: str, auteur: str, isbn: str) -> tuple[bool, str]:
        titre = titre.strip()
        auteur = auteur.strip()
        isbn = isbn.strip()

        if not titre or not auteur or not isbn:
            return False, "Tous les champs (titre, auteur, ISBN) sont obligatoires."
        if self._contient_separateur([titre, auteur, isbn]):
            return False, "Le caractère '|' n'est pas autorisé dans les champs."
        if self.bibliotheque.find_book_by_isbn(isbn) is not None:
            return False, f"Un livre avec l'ISBN {isbn} existe déjà."

        self.bibliotheque.add_book(bp.Book(titre, auteur, isbn))
        return True, f"Livre « {titre} » ajouté avec succès."

    def supprimer_livre(self, isbn: str) -> tuple[bool, str]:
        isbn = isbn.strip()
        if not isbn:
            return False, "Veuillez indiquer un ISBN."

        livre = self.bibliotheque.find_book_by_isbn(isbn)
        if livre is None:
            return False, f"Aucun livre trouvé avec l'ISBN {isbn}."
        if not livre.is_available():
            return False, "Impossible de supprimer un livre actuellement emprunté."

        titre = livre.get_title()
        if self.bibliotheque.remove_book(isbn):
            return True, f"Livre « {titre} » supprimé avec succès."
        return False, "Erreur lors de la suppression du livre."

    def obtenir_tous_les_utilisateurs(self):
        return self.bibliotheque.get_all_users()

    def ajouter_utilisateur(self, nom: str, id_utilisateur: str) -> tuple[bool, str]:
        nom = nom.strip()
        id_utilisateur = id_utilisateur.strip()

        if not nom or not id_utilisateur:
            return False, "Le nom et l'identifiant utilisateur sont obligatoires."
        if self._contient_separateur([nom, id_utilisateur]):
            return False, "Le caractère '|' n'est pas autorisé dans les champs."
        if self.bibliotheque.find_user_by_id(id_utilisateur) is not None:
            return False, f"Un utilisateur avec l'ID {id_utilisateur} existe déjà."

        self.bibliotheque.add_user(bp.User(nom, id_utilisateur))
        return True, f"Utilisateur « {nom} » ajouté avec succès."

    def emprunter_livre(self, isbn: str, id_utilisateur: str) -> tuple[bool, str]:
        isbn = isbn.strip()
        id_utilisateur = id_utilisateur.strip()

        if not isbn or not id_utilisateur:
            return False, "Veuillez sélectionner un livre et un utilisateur."
        if self.bibliotheque.find_book_by_isbn(isbn) is None:
            return False, f"Livre introuvable (ISBN : {isbn})."
        if self.bibliotheque.find_user_by_id(id_utilisateur) is None:
            return False, f"Utilisateur introuvable (ID : {id_utilisateur})."

        if self.bibliotheque.check_out_book(isbn, id_utilisateur):
            return True, f"Livre {isbn} emprunté par {id_utilisateur}."
        return False, "Ce livre n'est pas disponible pour l'emprunt."

    def retourner_livre(self, isbn: str) -> tuple[bool, str]:
        isbn = isbn.strip()
        if not isbn:
            return False, "Veuillez indiquer l'ISBN du livre à retourner."
        if self.bibliotheque.find_book_by_isbn(isbn) is None:
            return False, f"Livre introuvable (ISBN : {isbn})."

        if self.bibliotheque.return_book(isbn):
            return True, f"Livre {isbn} retourné avec succès."
        return False, "Ce livre n'est pas actuellement emprunté."

    def sauvegarder(self) -> tuple[bool, str]:
        if self.gestionnaire.save_library_data(self.bibliotheque):
            return True, "Données sauvegardées avec succès."
        return False, "Erreur lors de la sauvegarde des données."

    def creer_sauvegarde(self) -> tuple[bool, str]:
        try:
            self.gestionnaire.create_backup()
            return True, "Fichiers de sauvegarde (.backup) créés avec succès."
        except Exception as erreur:
            return False, f"Erreur lors de la création de la sauvegarde : {erreur}"
