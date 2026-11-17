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

# Interface graphique (Python)

L'interface utilise PyQt5 et appelle le code C++ via pybind11.
Installez les dépendances puis compilez le module Python :

```
$ python3 -m pip install -r requirements-ui.txt
$ cmake -S . -B build
$ cmake --build build
```

Lancez l'interface depuis le répertoire `agent/` :

```
$ python3 ui/main.py -d data
```

Le répertoire passé à `-d` doit contenir `books.txt` et `users.txt`.

Si l'affichage X11 n'est pas disponible dans le conteneur, forcez Wayland :

```
$ QT_QPA_PLATFORM=wayland python3 ui/main.py -d data
```
