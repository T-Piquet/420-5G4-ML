# Bibliothèque personnelle

Gérez un catalogue de livres et ses emprunts depuis le terminal ou une fenêtre CustomTkinter. Les deux interfaces réutilisent la logique C++.

## Fonctionnalités

- Ajouter et supprimer des livres, rechercher par titre ou auteur, et afficher tous les livres ou seulement ceux qui sont disponibles.
- Trier les listes et les résultats par titre ou auteur sans modifier l’ordre enregistré du catalogue. En cas d’égalité, le tri conserve l’ordre relatif des livres.
- Ajouter et consulter les utilisateurs, emprunter et retourner des livres. Un livre emprunté affiche le nom de l’emprunteur, ou son ID si le nom est introuvable.
- Consulter les statistiques : total des livres, disponibilités, emprunts et nombre d’utilisateurs.
- Sauvegarder et recharger les données, créer une copie `.backup` et conserver un journal d’activités entre les sessions.

## Lancer le programme en ligne de commande

Dans le devcontainer, depuis la racine du dépôt, avec CMake 3.21+ et un compilateur C++17 :

```sh
cmake -S agent -B agent/build -DBIBLIOTHEQUE_BUILD_PYTHON=OFF
cmake --build agent/build
scratch="$(mktemp -d)"
cp agent/data/books.txt agent/data/users.txt "$scratch/"
./agent/build/bibliotheque --data-dir "$scratch"
```

Utilisez une copie des données d’exemple : la sauvegarde réécrit `books.txt` et `users.txt`. L’option 12 sauvegarde les données, l’option 13 copie les fichiers déjà sauvegardés et l’option 0 sauvegarde avant de quitter.

Sans `--data-dir` (ou `-d`), le catalogue démarre vide. La sauvegarde manuelle et la sauvegarde à la fermeture sont ignorées, avec un message explicite.

## Journal d’activités

Les deux interfaces créent `activity.log` au démarrage dans le répertoire donné par `-d`. Le CLI utilise le répertoire courant s’il est lancé sans `-d`.
Les ajouts et suppressions de livres, les emprunts et les retours réussis sont ajoutés au fichier avec l’heure locale.
Un retour consigne le livre tel qu’il était avant le retour pour conserver le
nom de l’emprunteur. Les entrées restent disponibles après chaque session.

## Interface graphique

La fenêtre CustomTkinter s’inspire de la [maquette](maquetteTPAI.png) et utilise pybind11 pour appeler le C++.

- **Catalogue** : choisissez **Tous les livres** ou **Livres disponibles**. La barre de recherche cherche dans le titre et l’auteur à la fois ; le menu **Trier par** est indépendant. Le bouton **Ajouter un livre** se trouve à côté de la recherche. Sélectionnez une ligne pour emprunter, retourner ou supprimer le livre.
- **Utilisateurs** et **Statistiques** : consultez les utilisateurs, ajoutez-en un ou affichez les compteurs de la bibliothèque.
- **Sauvegardes** : utilisez **Sauvegarder les données** pour écrire les changements et **Créer une sauvegarde** pour copier les fichiers déjà écrits sur disque. **Quitter** sauvegarde avant de fermer la fenêtre.

Dans le devcontainer, depuis la racine du dépôt (reconstruire le conteneur pour
installer les en-têtes Python, si nécessaire) :

```sh
python3 -m venv /tmp/bibliotheque-venv
py=/tmp/bibliotheque-venv/bin/python
"$py" -m pip install -r agent/requirements-gui.txt
cmake -S agent -B agent/build-gui -DBIBLIOTHEQUE_BUILD_PYTHON=ON \
  -DPython_EXECUTABLE="$py"
cmake --build agent/build-gui
scratch="$(mktemp -d)"
cp agent/data/books.txt agent/data/users.txt "$scratch/"
PYTHONPATH="$PWD/agent/build-gui" "$py" agent/gui.py --data-dir "$scratch"
```

La fenêtre nécessite un serveur d’affichage accessible depuis le conteneur.
Utilisez une seule session d’édition à la fois pour un même répertoire de données.
Le CLI se compile toujours seul avec `cmake -S agent -B agent/build` puis
`cmake --build agent/build`, sans dépendance Python.
