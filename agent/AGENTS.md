# Instructions pour les agents

## Vue d'ensemble

`agent/` contient le gestionnaire de bibliothèque personnelle : un coeur C++
(`book`, `user`, `library`, `filemanager`), un exécutable en ligne de commande
(`main.cpp`) et une interface graphique PyQt5 qui appelle le code C++ via
pybind11 (`bindings.cpp`, `ui/`).

## Structure

- `book.*`, `user.*`, `library.*`, `filemanager.*` : logique métier et
  persistance (fichiers `books.txt` / `users.txt` au format `|`).
- `main.cpp` : menu interactif en console (l'exécutable `bibliotheque`).
- `bindings.cpp` : module Python `bibliotheque_py` (construit dans `build/`).
  Les accesseurs renvoient des **copies** de `Book` / `User` : ne pas exposer
  de pointeurs bruts vers la bibliothèque C++.
- `ui/` : interface PyQt5. `service.py` contient les règles de l'interface
  (validation, résolution des noms, sauvegarde automatique) ; `pages.py` décrit
  les pages ; `window.py` gère la navigation ; `theme.py` la palette et le QSS.
- `maquette/AiReview/` : maquettes de référence des pages 1 à 7.
- `data/` : jeu de données de démonstration (41 livres, 25 utilisateurs).

## Compilation

Depuis `agent/` :

```sh
cmake -S . -B build
cmake --build build
```

- Le module Python est produit dans `build/bibliotheque_py.<abi>.so`.
- Cible CLI seulement : `cmake -S . -B build -DBUILD_PYTHON_BINDINGS=OFF`.
- pybind11 est découvert via `python3 -m pybind11 --cmakedir` s'il est installé
  avec pip. Le module est lié à la version de Python utilisée pour compiler
  (3.13 dans ce conteneur) : **recompiler** si l'interpréteur change.

## Lancement de l'interface

Depuis `agent/` :

```sh
python3 ui/main.py -d data
```

- `-d` doit pointer vers un répertoire contenant `books.txt` et `users.txt`.
- Si X11 n'est pas disponible (cas de ce conteneur, `DISPLAY=1` injoignable) :

```sh
QT_QPA_PLATFORM=wayland python3 ui/main.py -d data
```

## Points d'attention

- **Fins de ligne** : les fichiers de données du dépôt sont en CRLF.
  `Book::fromFileFormat` et `User::fromFileFormat` suppriment le `\r` final ;
  ne pas retirer ce traitement. La sauvegarde réécrit les fichiers en LF : pour
  les tests, travailler sur une **copie** dans `/tmp` afin de ne pas modifier
  `data/books.txt` et `data/users.txt`.
- **Recherche** : les méthodes C++ sont exposées, mais l'interface filtre les
  copies en Python avec `casefold()` (insensible à la casse et aux accents).
  La résolution d'un emprunteur par son nom se fait aussi en Python
  (`LibraryService.find_user_by_name`) ; la mutation reste faite par
  `Library::checkOutBook`.
- **Persistance** : pas de bouton « Enregistrer » dans les maquettes, donc
  sauvegarde automatique après chaque mutation et à la fermeture de la fenêtre.
- **Style** : les boutons utilisent `border-radius: 18px` ; Qt ignore le rayon
  si `border-radius >= hauteur / 2`. `theme.py` fixe donc `min-height: 22px`
  avec un padding vertical de 9 px pour garder des boutons arrondis.
- **Erreurs** : les messages d'erreur sont affichés dans le panneau
  (`QLabel#ErrorLabel`), pas dans des boîtes de dialogue.

## Vérifications

- Compilation propre attendue avec `-Wall -Wextra -Wpedantic`.
- Il n'y a pas de suite de tests ni de CI dans le dépôt. Pour valider :
  tests ponctuels du module (`PYTHONPATH=build`), test `QT_QPA_PLATFORM=offscreen`
  des pages, et vérification que `build/bibliotheque` affiche toujours les
  statistiques attendues.
