import shutil
from pathlib import Path

import pytest

from gui.controleur import ControleurBibliotheque

DOSSIER_DONNEES = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def controleur(tmp_path):
    shutil.copy2(DOSSIER_DONNEES / "books.txt", tmp_path / "books.txt")
    shutil.copy2(DOSSIER_DONNEES / "users.txt", tmp_path / "users.txt")
    return ControleurBibliotheque(tmp_path)


def test_repertoire_inexistant(tmp_path):
    with pytest.raises(FileNotFoundError):
        ControleurBibliotheque(tmp_path / "introuvable")


def test_statistiques_initiales(controleur):
    stats = controleur.obtenir_statistiques()
    assert stats == {
        "total_livres": 41,
        "disponibles": 27,
        "empruntes": 14,
        "total_utilisateurs": 25,
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
    assert controleur.obtenir_statistiques()["total_livres"] == 42

    ok, _ = controleur.supprimer_livre("9782253096337")
    assert ok is False

    ok, _ = controleur.supprimer_livre("9782266320542")
    assert ok is True
    assert controleur.obtenir_statistiques()["total_livres"] == 41


def test_validation_ajout_utilisateur(controleur):
    ok, _ = controleur.ajouter_utilisateur("", "USR999")
    assert ok is False

    ok, _ = controleur.ajouter_utilisateur("Nom|Bad", "USR999")
    assert ok is False

    ok, _ = controleur.ajouter_utilisateur("Doublon", "USR001")
    assert ok is False

    ok, _ = controleur.ajouter_utilisateur("Nadia Karim", "USR999")
    assert ok is True
    assert controleur.obtenir_statistiques()["total_utilisateurs"] == 26


def test_emprunt_retour_sauvegarde_et_backup(controleur):
    ok, _ = controleur.emprunter_livre("9782070612758", "USR015")
    assert ok is True
    assert controleur.obtenir_statistiques()["empruntes"] == 15
    assert len(controleur.obtenir_livres_empruntes()) == 15

    ok, _ = controleur.emprunter_livre("9782070612758", "USR016")
    assert ok is False

    ok, _ = controleur.retourner_livre("9782070612758")
    assert ok is True
    assert controleur.obtenir_statistiques()["empruntes"] == 14

    ok, _ = controleur.sauvegarder()
    assert ok is True

    ok, _ = controleur.creer_sauvegarde()
    assert ok is True
    assert (controleur.repertoire_donnees / "books.txt.backup").exists()
    assert (controleur.repertoire_donnees / "users.txt.backup").exists()
