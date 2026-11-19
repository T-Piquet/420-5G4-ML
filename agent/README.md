# Construire le projet
Vous pouvez utiliser un dev container de base C++ de VScode.
Le projet utilise cmake, pensez à l'inclure dans votre dev container.

Voici les lignes de commandes pour compiler le projet:
```
$ mkdir build
$ cd build
$ cmake ..
$ make
```

# Répertoire data

Il contient 2 fichiers `books.txt`et `users.txt` que vous pouvez utilisez pour tester votre code.
Pour ca il suffit de donner chemin vers le repertoire data avec l'application `bibliotheque -d <chemin verrs data>`

# Interface graphique

L'interface CustomTkinter utilise les bindings Python du projet. Depuis `agent/` :

```
$ .venv/bin/pip install -r requirements.txt
$ cmake -S . -B build
$ cmake --build build -j
$ .venv/bin/python -m interface -d data
```

Le module compilé est cherché automatiquement dans `build/`. Les écrans Livres,
Utilisateurs et Paramètres sont fonctionnels. L'onglet Paramètres permet de
sauvegarder les données, de créer une sauvegarde `.backup` (après sauvegarde) et
d'afficher les statistiques de la bibliothèque. Les modifications sont aussi
sauvegardées à la fermeture de la fenêtre. Pour tester sans modifier les données
du projet, utiliser une copie temporaire du répertoire `data`.
