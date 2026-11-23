# GUI — application de test

Interface graphique minimale (une seule fenêtre) pour la bibliothèque,
construite avec [CustomTkinter](https://customtkinter.tomschimansky.com/).
Elle lit et écrit les mêmes fichiers que la CLI C++ (`agent/data/books.txt`,
`agent/data/users.txt`), donc les deux outils restent interchangeables.

## Installation (venv local)

```bash
cd agent/GUI
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

## Lancement

```bash
.venv/bin/python app.py
```

Sans argument, les données sont lues depuis `agent/data/` (chemin calculé
relativement au script, indépendant du répertoire courant). Pour tester sur une
copie :

```bash
.venv/bin/python app.py --data-dir /tmp/biblio-test
```

Un affichage X11 est nécessaire (le devcontainer de `agent/` le fournit via
`DISPLAY`).

## Fonctionnalités

- liste des livres avec recherche instantanée par titre ou auteur ;
- suppression d'un livre, avec confirmation ;
- sauvegarde automatique après suppression ;
- bascule thème clair / sombre.

Cette version est un test d'intégration de CustomTkinter : l'ajout de livres ou
d'utilisateurs, l'emprunt et le retour ne sont pas exposés dans l'interface
(les méthodes correspondantes restent disponibles dans `data_store.py`).

## Formats des données

- `books.txt` : `titre|auteur|isbn|1ou0|idEmprunteur`
- `users.txt` : `nom|id|isbn1,isbn2` (`|` final conservé même sans emprunt)

Le caractère `|` est refusé dans les champs saisis. Contrairement à la CLI C++,
la suppression d'un livre retire aussi son ISBN des utilisateurs.

## Limites

- Pas de pybind11 : la persistance est réimplémentée en Python (`data_store.py`).
- Pas de tests automatisés de l'interface ; seul le chargement/sauvegarde est
  vérifiable sans affichage.
- Les données fournies contiennent une incohérence préexistante : *Indiana*
  (`9782070360093`) est marqué emprunté par `USR010`, alors que `USR010` liste
  *Corinne* (`9782070360086`). L'application ne la corrige pas automatiquement.
