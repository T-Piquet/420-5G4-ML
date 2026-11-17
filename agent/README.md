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


# Lancer l'interface graphique (GUI)

Après avoir compilé le projet avec CMake (pour générer le module `bibliotheque_cpp`), lancez l'interface Python :
```bash
cd gui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
.