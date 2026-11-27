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

# Lancement facile

Le script `bibliotheque-ui` compile automatiquement le projet au premier
lancement puis ouvre l'interface graphique :
```
$ ./bibliotheque-ui
```
Pour utiliser un autre dossier de donnees :
```
$ ./bibliotheque-ui -d /chemin/vers/data
```

Le programme C++ classique reste disponible dans `build/bibliotheque` :
```
$ ./build/bibliotheque -d data
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

## Simplicite d'utilisation

- **Ajouter un livre** : entrez seulement le titre et l'auteur. L'ISBN est
  pre-rempli automatiquement avec un numero a 13 chiffres qui suit le meme
  format que les livres existants (ex. 9782253096338). La touche Entree valide.
- **Ajouter un utilisateur** : entrez seulement le nom. L'identifiant est
  pre-rempli automatiquement (USR001, USR002, ...).
- **Retourner un livre** : un seul clic, aucune confirmation.
- **Annuler** : un bouton unique annule la derniere action (jusqu'a 25 actions).
- Gros boutons et gros champs pour une prise en main immediate.
