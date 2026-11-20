import gc

import pytest

import bibliotheque_py as bp

LIVRES_EXEMPLE = "\n".join([
    "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|",
    "Les Misérables|Victor Hugo|9782253096337|0|USR001",
    "Notre-Dame de Paris|Victor Hugo|9782253002864|1|",
    "L'Étranger|Albert Camus|9782070360024|1|",
]) + "\n"

UTILISATEURS_EXEMPLE = "\n".join([
    "Marie Dubois|USR001|9782253096337",
    "Jean Martin|USR002|",
    "Alexandra Dumont|USR015|",
]) + "\n"


@pytest.fixture
def contexte_bibliotheque(tmp_path):
    fichier_livres = tmp_path / "books.txt"
    fichier_utilisateurs = tmp_path / "users.txt"
    fichier_livres.write_text(LIVRES_EXEMPLE, encoding="utf-8")
    fichier_utilisateurs.write_text(UTILISATEURS_EXEMPLE, encoding="utf-8")

    bibliotheque = bp.Library()
    gestionnaire = bp.FileManager(str(fichier_livres), str(fichier_utilisateurs))
    assert gestionnaire.load_library_data(bibliotheque) is True
    return bibliotheque, gestionnaire, fichier_livres, fichier_utilisateurs


def test_chargement_fixtures(contexte_bibliotheque):
    bibliotheque, _, _, _ = contexte_bibliotheque

    total = bibliotheque.get_total_books()
    disponibles = bibliotheque.get_available_book_count()
    empruntes = bibliotheque.get_checked_out_book_count()
    utilisateurs = bibliotheque.get_all_users()

    assert total == 4
    assert disponibles == 3
    assert empruntes == 1
    assert disponibles + empruntes == total
    assert len(bibliotheque.get_all_books()) == total
    assert len(bibliotheque.get_available_books()) == disponibles
    assert len(utilisateurs) == 3


def test_gestion_livres(contexte_bibliotheque):
    bibliotheque, _, _, _ = contexte_bibliotheque

    nouveau = bp.Book("Fondation", "Isaac Asimov", "9782070360536")
    assert nouveau.get_title() == "Fondation"
    assert nouveau.get_author() == "Isaac Asimov"
    assert nouveau.get_isbn() == "9782070360536"
    assert nouveau.is_available() is True
    assert nouveau.get_borrower_id() == ""
    assert "Fondation" in repr(nouveau)
    assert "Fondation" in nouveau.to_string()

    bibliotheque.add_book(nouveau)
    assert bibliotheque.get_total_books() == 5

    trouve = bibliotheque.find_book_by_isbn("9782070360536")
    assert trouve is not None
    assert trouve.get_title() == "Fondation"

    assert bibliotheque.find_book_by_isbn("ISBN-INEXISTANT") is None

    par_titre = bibliotheque.search_books_by_title("fonda")
    assert len(par_titre) == 1
    assert par_titre[0].get_isbn() == "9782070360536"

    par_auteur = bibliotheque.search_books_by_author("victor hugo")
    assert len(par_auteur) == 2
    assert all("Hugo" in livre.get_author() for livre in par_auteur)

    assert bibliotheque.remove_book("9782070360536") is True
    assert bibliotheque.remove_book("9782070360536") is False
    assert bibliotheque.get_total_books() == 4


def test_gestion_utilisateurs(contexte_bibliotheque):
    bibliotheque, _, _, _ = contexte_bibliotheque

    utilisateur = bp.User("Amine Benali", "USR999")
    assert utilisateur.get_name() == "Amine Benali"
    assert utilisateur.get_user_id() == "USR999"
    assert utilisateur.get_borrowed_books() == []
    assert utilisateur.get_number_of_borrowed_books() == 0
    assert "Amine Benali" in repr(utilisateur)

    bibliotheque.add_user(utilisateur)
    assert len(bibliotheque.get_all_users()) == 4

    trouve = bibliotheque.find_user_by_id("USR999")
    assert trouve is not None
    assert trouve.get_name() == "Amine Benali"
    assert bibliotheque.find_user_by_id("USR-INCONNU") is None

    marie = bibliotheque.find_user_by_id("USR001")
    assert marie is not None
    assert marie.has_borrowed_book("9782253096337") is True
    assert marie.get_number_of_borrowed_books() == 1


def test_emprunts_et_retours(contexte_bibliotheque):
    bibliotheque, _, _, _ = contexte_bibliotheque

    isbn_dispo = "9782070612758"
    id_utilisateur = "USR015"

    assert bibliotheque.check_out_book(isbn_dispo, id_utilisateur) is True

    livre = bibliotheque.find_book_by_isbn(isbn_dispo)
    utilisateur = bibliotheque.find_user_by_id(id_utilisateur)
    assert livre.is_available() is False
    assert livre.get_borrower_id() == id_utilisateur
    assert utilisateur.has_borrowed_book(isbn_dispo) is True

    assert bibliotheque.check_out_book(isbn_dispo, "USR002") is False
    assert bibliotheque.check_out_book("ISBN-INCONNU", id_utilisateur) is False
    assert bibliotheque.check_out_book(isbn_dispo, "USR-INCONNU") is False

    assert bibliotheque.return_book(isbn_dispo) is True
    assert livre.is_available() is True
    assert livre.get_borrower_id() == ""
    assert utilisateur.has_borrowed_book(isbn_dispo) is False

    assert bibliotheque.return_book(isbn_dispo) is False
    assert bibliotheque.return_book("ISBN-INCONNU") is False


def test_persistance_et_sauvegarde(contexte_bibliotheque):
    bibliotheque, gestionnaire, fichier_livres, fichier_utilisateurs = contexte_bibliotheque

    bibliotheque.add_book(bp.Book("Dune", "Frank Herbert", "9782266320542"))
    bibliotheque.add_user(bp.User("Claire Moreau", "USR100"))
    assert bibliotheque.check_out_book("9782266320542", "USR100") is True
    assert gestionnaire.save_library_data(bibliotheque) is True

    nouvelle_biblio = bp.Library()
    assert gestionnaire.load_library_data(nouvelle_biblio) is True
    assert nouvelle_biblio.get_total_books() == 5
    assert len(nouvelle_biblio.get_all_users()) == 4

    dune = nouvelle_biblio.find_book_by_isbn("9782266320542")
    claire = nouvelle_biblio.find_user_by_id("USR100")
    assert dune is not None
    assert dune.is_available() is False
    assert dune.get_borrower_id() == "USR100"
    assert claire is not None
    assert claire.has_borrowed_book("9782266320542") is True

    gestionnaire.create_backup()
    gestionnaire.create_backup()
    assert gestionnaire.file_exists(str(fichier_livres) + ".backup") is True
    assert gestionnaire.file_exists(str(fichier_utilisateurs) + ".backup") is True


def test_stabilite_memoire_references(contexte_bibliotheque):
    bibliotheque, _, _, _ = contexte_bibliotheque

    for _ in range(5):
        livres = bibliotheque.get_all_books()
        utilisateurs = bibliotheque.get_all_users()
        livre = bibliotheque.find_book_by_isbn("9782070612758")
        utilisateur = bibliotheque.find_user_by_id("USR001")

        assert len(livres) == 4
        assert len(utilisateurs) == 3
        assert livre is not None and livre.get_title() == "Le Petit Prince"
        assert utilisateur is not None and utilisateur.get_name() == "Marie Dubois"

        del livres, utilisateurs, livre, utilisateur
        gc.collect()

    assert bibliotheque.get_total_books() == 4
    assert bibliotheque.find_book_by_isbn("9782070612758").get_title() == "Le Petit Prince"
