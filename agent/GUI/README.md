# GUI — application de test

Interface graphique (une seule fenêtre) pour la bibliothèque, construite avec
[CustomTkinter](https://customtkinter.tomschimansky.com/). Elle lit et écrit les
mêmes fichiers que la CLI C++ (`agent/data/books.txt`, `agent/data/users.txt`),
donc les deux outils restent interchangeables.

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

- bandeau « Gestionnaire de la Bibliothèque » en haut de chaque page ;
- page Utilisateurs en lecture seule : cartes sur quatre colonnes avec nom,
  identifiant et nombre de livres empruntés ;
- statistiques réelles en pied de page : livres, livres disponibles, livres
  empruntés et utilisateurs ;
- boutons `Utilisateur +`, `Voir livres` et `Créer sauvegarde` présents mais
  encore inactifs ;
- thème beige et vert unique, sans mode sombre.

Les pages Livres, l'ajout d'utilisateur et de livre, l'emprunt, le retour et la
sauvegarde manuelle seront ajoutés dans les prochaines étapes. Les méthodes
correspondantes existent déjà dans `data_store.py`.

## Apparence

Le thème est centralisé dans `theme.py` (palette, polices, arrondis). Garamond
est la police voulue ; si elle est absente du système, la première famille
disponible parmi `EB Garamond` et `DejaVu Serif` est utilisée automatiquement.

## Formats des données

- `books.txt` : `titre|auteur|isbn|1ou0|idEmprunteur`
- `users.txt` : `nom|id|isbn1,isbn2` (`|` final conservé même sans emprunt)

Le caractère `|` est refusé dans les champs saisis. Contrairement à la CLI C++,
la suppression d'un livre retire aussi son ISBN des utilisateurs.

## Limites

- Pas de pybind11 : la persistance est réimplémentée en Python (`data_store.py`).
- Pas de tests automatisés de l'interface ; seul le chargement/sauvegarde est
  vérifiable sans affichage.
