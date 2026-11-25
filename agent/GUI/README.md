# GUI — application de test

Interface graphique (une seule fenêtre) pour la bibliothèque, construite avec
[CustomTkinter](https://customtkinter.tomschimansky.com/). Elle lit et écrit les
mêmes fichiers que la CLI C++ (`agent/data/books.txt`, `agent/data/users.txt`)
via le moteur partagé `bibliotheque_core`, donc les deux outils restent
interchangeables.

## Installation (venv local)

```bash
cd agent/GUI
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

Le module C++ `bibliotheque_core` doit être construit au préalable ; la commande
complète est décrite dans le `README.md` du dossier `agent/` (section
« Construire l'interface C++ et la GUI »).

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
- page Livres, écran principal : cartes sur trois colonnes avec titre, auteur,
  ISBN discret et boutons `Emprunter` / `Retourner` plus une corbeille, pour
  l'instant inertes ;
- barre `Rechercher` : le texte n'est pris en compte qu'au clic sur la loupe ;
  la recherche porte sur les titres et les noms d'auteurs (sous-chaîne, casse
  ASCII ignorée) et n'affiche que les cartes correspondantes. Une requête vide
  ramène toute la bibliothèque ; sans résultat, la grille affiche la requête.
  La touche `Entrée` ne lance rien avec du texte ; sur un champ vide, elle
  réaffiche toutes les cartes ;
- filtre `Tous` / `Disponibles`, appliqué immédiatement et combiné à la
  recherche ; la liste des disponibles vient du moteur C++ (`getAvailableBooks`)
  et `Entrée` sur un champ vide conserve le filtre ; bouton `Livre +` encore
  inactif ;
- page Utilisateurs en lecture seule : cartes sur quatre colonnes avec nom,
  identifiant et nombre de livres empruntés ;
- statistiques réelles en pied de page : livres, livres disponibles, livres
  empruntés et utilisateurs ;
- bouton `Utilisateur +` qui ouvre un panneau latéral d'ajout :
  - nom obligatoire, sans chiffres, avec majuscule automatique en début de mot
    et après un tiret (pas après une apostrophe) ;
  - identifiant `USRXXX` généré automatiquement ;
  - message d'erreur ou de confirmation dans le panneau, avec mise à jour
    immédiate de la liste et des statistiques ;
  - bouton `Annuler` pour fermer le panneau ;
- navigation entre les pages via `Voir utilisateurs` et `Voir livres` ;
- bouton `Créer sauvegarde`, présent sur les deux pages : copie `books.txt` et
  `users.txt` dans leurs `.backup` via le moteur C++, puis affiche dans le pied
  de page « Sauvegarde créée. », « Aucun fichier à sauvegarder. » ou l'erreur
  (terracotta). Un nouveau clic écrase les backups précédents ;
- thème beige et vert unique, sans mode sombre.

L'ajout de livre, l'emprunt, le retour et la suppression seront ajoutés dans les
prochaines étapes. Les méthodes correspondantes existent déjà dans
`data_store.py`.

## Apparence

Le thème est centralisé dans `theme.py` (palette, polices, arrondis). Garamond
est la police voulue ; si elle est absente du système, la première famille
disponible parmi `EB Garamond` et `DejaVu Serif` est utilisée automatiquement.

## Formats des données

- `books.txt` : `titre|auteur|isbn|1ou0|idEmprunteur`
- `users.txt` : `nom|id|isbn1,isbn2` (`|` final conservé même sans emprunt)

Le caractère `|` est refusé dans les champs saisis. À l'ajout d'un utilisateur,
l'identifiant `USRXXX` est généré automatiquement et le nom est mis en forme
avant l'écriture. La suppression d'un livre retire aussi son ISBN des
utilisateurs.

## Limites

- Le module `bibliotheque_core` (pybind11) est obligatoire : sans lui,
  l'application échoue à l'import, sans repli vers Python.
- Pas de tests automatisés de l'interface ; seul le chargement/sauvegarde est
  vérifiable sans affichage.
