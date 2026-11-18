# Bibliothèque

Application console C++17 de gestion de bibliothèque, avec une interface graphique Python (CustomTkinter) et un module pybind11 `bibliotheque_py`.

## Prérequis

- CMake ≥ 3.21 et compilateur C++17.
- Python 3 avec `venv` et `tkinter`.
- pybind11 (`pybind11-dev`, `python3-pybind11` ou équivalent).
- CustomTkinter via `gui/requirements.txt`.
- X11 / `DISPLAY` pour la GUI, fourni par le devcontainer.

Vous pouvez utiliser un dev container C++ de VS Code ; pensez à y inclure CMake, Python, pybind11 et le support X11.

## Compilation du programme console

```bash
cd agent
cmake -S . -B build
cmake --build build -j
```

Les commandes équivalentes `mkdir build && cd build && cmake .. && make` fonctionnent aussi.

## Compilation du module Python

Créer le venv et installer les dépendances :

```bash
cd agent/gui
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Puis compiler le module depuis `agent/` :

```bash
cd ..
cmake -S . -B build -DBUILD_PYTHON_MODULE=ON \
  -DPython_EXECUTABLE="$PWD/gui/.venv/bin/python"
cmake --build build -j
```

Si Python ou pybind11 n'est pas disponible, la console se compile quand même : un avertissement est émis et la GUI ne peut pas charger le module.

## Lancement

Console :

```bash
cd agent
./build/bibliotheque -d data
```

GUI :

```bash
cd agent
./gui/.venv/bin/python gui/main.py -d data
```

Le chemin passé à `-d` est relatif au répertoire courant. Sans `-d`, la GUI utilise `agent/data`. Pour tester sans modifier les données suivies, copier `data/` dans un répertoire temporaire et passer ce chemin à `-d`.

Vérification du module :

```bash
./gui/.venv/bin/python python/test_bibliotheque_py.py
```

## Répertoire data

`data/` contient `books.txt` et `users.txt`, utilisés par la console et la GUI. L'application les charge au démarrage et les sauvegarde uniquement sur action explicite (menu 12 de la console, bouton Sauvegarder de la GUI).

## Structure

```text
agent/
├── main.cpp, book.*, user.*, library.*, filemanager.*
├── CMakeLists.txt
├── data/              # books.txt, users.txt
├── gui/               # interface CustomTkinter, venv local
├── python/            # bindings.cpp, test_bibliotheque_py.py
├── maquettes/         # maquettes Draw.io et PNG
├── chatsLogs/         # journaux de développement
└── build/             # généré, ignoré par git
```

## Remarques

- `build/`, `gui/.venv/`, `*.backup` et `data_test/` sont ignorés par git.
- Les modifications restent en mémoire jusqu'à un clic sur Sauvegarder ; à la fermeture, la GUI propose de sauvegarder s'il y a des modifications.
- Voir `AGENTS.md` pour les détails de développement et les limites connues.