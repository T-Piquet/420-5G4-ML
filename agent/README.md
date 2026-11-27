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

# Interface graphique Python

Le module pybind11 `bibliotheque_core` est compile en meme temps que l'application
lorsque pybind11 est disponible (il est deja installe dans le dev container).
L'interface Tkinter utilise ce module et propose un theme sombre.

Apres la compilation:
```
$ cd ..
$ python3 ui.py --data-dir data
```

Sans l'option `--data-dir`, l'interface cherche automatiquement un repertoire
contenant `books.txt` / `users.txt` (`data`, `../data` ou `agent/data`).

Si le module a ete compile dans un autre repertoire, indiquez son chemin:
```
$ BIBLIOTHEQUE_CORE_PATH=/chemin/vers/build python3 ui.py -d data
```

Fonctionnalites de l'interface: ajout/suppression de livres, recherche et filtres,
ajout d'utilisateurs, emprunts et retours, statistiques, enregistrement et sauvegarde.

## Mode securise (enfant)

L'interface demarre en **mode securise** : les operations qui modifient la
bibliotheque sont verrouillees (consulation, recherche et statistiques restent
disponibles). Pour les activer, cliquez sur `Deverrouiller` et resolvez le petit
calcul reserve aux adultes. Le bouton `Verrouiller` reactive immediatement la
protection.

Les actions destructives demandent toujours une confirmation, la fermeture de la
fenetre est confirmee et les dernieres modifications peuvent etre annulees avec
le bouton `Annuler`.
