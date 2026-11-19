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

# Interface Python (pybind11)

L'interface customtkinter se trouve dans `UI/`. Elle s'appuie sur le coeur C++
du projet via le module `bibliotheque_core`, compilé avec pybind11.

```bash
cd UI
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cd ..
./bindings/build.sh
cd UI
.venv/bin/python main.py
```

Voir `UI/README.md` pour la structure MVC, le format des données et les tests.