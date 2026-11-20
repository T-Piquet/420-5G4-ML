import pytest

from gui.controleur import ControleurBibliotheque

LIVRES_EXEMPLE = "\n".join([
    "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|",
    "Les Misérables|Victor Hugo|9782253096337|0|USR001",
    "L'Étranger|Albert Camus|9782070360024|1|",
]) + "\n"

UTILISATEURS_EXEMPLE = "\n".join([
    "Marie Dubois|USR001|9782253096337",
    "Jean Martin|USR002|",
    "Alexandra Dumont|USR015|",
]) + "\n"


@pytest.fixture
def controleur(tmp_path):
    (tmp_path / "books.txt").write_text(LIVRES_EXEMPLE, encoding="utf-8")
    (tmp_path / "users.txt").write_text(UTILISATEURS_EXEMPLE, encoding="utf-8")
    return ControleurBibliotheque(tmp_path)


def test_repertoire_inexistant(tmp_path):
    with pytest.raises(FileNotFoundError):
        ControleurBibliotheque(tmp_path / "introuvable")


def test_statistiques_initiales(controleur):
    stats = controleur.obtenir_statistiques()
    assert stats == {
        "total_livres": 3,
        "disponibles": 2,
        "empruntes": 1,
        "total_utilisateurs": 3,
    }


def test_validation_ajout_et_suppression_livre(controleur):
    ok, _ = controleur.ajouter_livre("", "Auteur", "12345")
    assert ok is False

    ok, _ = controleur.ajouter_livre("Titre|Invalide", "Auteur", "12345")
    assert ok is False

    ok, _ = controleur.ajouter_livre("Le Petit Prince", "Auteur", "9782070612758")
    assert ok is False

    ok, _ = controleur.ajouter_livre("Dune", "Frank Herbert", "9782266320542")
    assert ok is True
    assert controleur.obtenir_statistiques()["total_livres"] == 4

    ok, _ = controleur.supprimer_livre("9782253096337")
    assert ok is False

    ok, _ = controleur.supprimer_livre("9782266320542")
    assert ok is True
    assert controleur.obtenir_statistiques()["total_livres"] == 3


def test_validation_ajout_utilisateur(controleur):
    ok, _ = controleur.ajouter_utilisateur("", "USR999")
    assert ok is False

    ok, _ = controleur.ajouter_utilisateur("Nom|Bad", "USR999")
    assert ok is False

    ok, _ = controleur.ajouter_utilisateur("Doublon", "USR001")
    assert ok is False

    ok, _ = controleur.ajouter_utilisateur("Nadia Karim", "USR999")
    assert ok is True
    assert controleur.obtenir_statistiques()["total_utilisateurs"] == 4


def test_emprunt_retour_sauvegarde_et_backup(controleur):
    ok, _ = controleur.emprunter_livre("9782070612758", "USR015")
    assert ok is True
    assert controleur.obtenir_statistiques()["empruntes"] == 2
    assert len(controleur.obtenir_livres_empruntes()) == 2

    ok, _ = controleur.emprunter_livre("9782070612758", "USR002")
    assert ok is False

    ok, _ = controleur.retourner_livre("9782070612758")
    assert ok is True
    assert controleur.obtenir_statistiques()["empruntes"] == 1

    ok, _ = controleur.sauvegarder()
    assert ok is True

    ok, _ = controleur.creer_sauvegarde()
    assert ok is True
    assert (controleur.repertoire_donnees / "books.txt.backup").exists()
    assert (controleur.repertoire_donnees / "users.txt.backup").exists()


def test_version_donnees_incremente_sur_mutations(controleur):
    assert controleur.version_donnees == 0
    controleur.obtenir_statistiques()
    assert controleur.version_donnees == 0

    controleur.ajouter_livre("Dune", "Frank Herbert", "9782266320542")
    assert controleur.version_donnees == 1

    controleur.ajouter_utilisateur("Nadia Karim", "USR999")
    assert controleur.version_donnees == 2

    controleur.emprunter_livre("9782266320542", "USR999")
    assert controleur.version_donnees == 3

    controleur.retourner_livre("9782266320542")
    assert controleur.version_donnees == 4

    controleur.supprimer_livre("9782266320542")
    assert controleur.version_donnees == 5
