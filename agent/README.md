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

Depuis le dossier `agent/`, compilez le module C++ puis lancez l'interface :
```
$ cmake -S python_bindings -B build/python_bindings
$ cmake --build build/python_bindings
$ python3 -m venv .venv
$ .venv/bin/pip install -r requirements.txt
$ .venv/bin/python main.py -d data
```

`gui/` suit une structure MVC :

| Dossier | Rôle |
|---------|------|
| `gui/models/` | Accès à l'API C++ (`bibliotheque`) et entités |
| `gui/views/` | Fenêtre, pages et composants customtkinter |
| `gui/controllers/` | Relie les actions des vues au modèle |

Raccourcis : `Ctrl+K` pour chercher un livre, `Ctrl+S` pour enregistrer.
