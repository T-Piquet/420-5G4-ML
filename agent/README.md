# Bibliothèque personnelle

Gestion de bibliothèque en deux clients qui partagent le même moteur C++ et les
mêmes données :

- `bibliotheque` : application en ligne de commande, en C++17 ;
- `GUI/` : interface graphique Python (CustomTkinter), reliée au moteur C++ par
  pybind11 (`bindings.cpp`).

Les deux lisent et écrivent `data/books.txt` et `data/users.txt`, donc ils sont
interchangeables : une modification faite dans l'un est visible dans l'autre
après sauvegarde.

## Prérequis

Le devcontainer de `.devcontainer/` fournit l'essentiel : CMake ≥ 3.21,
compilateur C++17, Python 3, `pybind11-dev`, `python3-tk` et l'accès X11.
Hors devcontainer, installer ces paquets et disposer d'un affichage X11 pour la
GUI.

## Compiler la CLI C++

Depuis `agent/` :

```bash
cmake -S . -B build
cmake --build build -j
```

C'est l'équivalent de `mkdir build && cd build && cmake .. && make`.

```bash
./build/bibliotheque -d data/          # depuis agent/
agent/build/bibliotheque -d agent/data/  # depuis la racine du dépôt
```

Sans `-d`, la CLI démarre en **mode mémoire** : aucun chargement, aucune
sauvegarde, et les commandes 12 (sauvegarder) et 13 (backup) sont ignorées. En
mode fichier, la sauvegarde a lieu avec l'option 12 et à la sortie 0 ;
`Ctrl+C` perd les modifications non sauvegardées.

## Construire l'interface C++ et la GUI

Le module `bibliotheque_core` n'est pas versionné : il est produit dans `GUI/`
par le build. Depuis `agent/` :

```bash
python3 -m venv GUI/.venv
GUI/.venv/bin/pip install --upgrade pip
GUI/.venv/bin/pip install -r GUI/requirements.txt

cmake -S . -B build \
  -DBUILD_PYTHON_BINDINGS=ON \
  -DPython_EXECUTABLE="$PWD/GUI/.venv/bin/python" \
  -Dpybind11_DIR=/usr/lib/cmake/pybind11
cmake --build build -j
```

Contrôle de l'import :

```bash
cd GUI && .venv/bin/python -c "import bibliotheque_core as b; print(b.__version__)"
# 0.1.0
```

Si `build/` a déjà été configuré sans l'option, relancer la commande `cmake`
ci-dessus : un simple `cmake --build` ne régénère pas le module.

## Lancer la GUI

```bash
cd GUI
.venv/bin/python app.py
```

Sans argument, les données sont lues depuis `agent/data/` (chemin calculé
relativement au script). Pour tester sur une copie :

```bash
.venv/bin/python app.py --data-dir /tmp/biblio-test
```

Le détail des écrans, du thème et des limites est dans `GUI/README.md`.

## Architecture

| Élément | Rôle |
|---|---|
| `main.cpp` | menu et boucle de la CLI |
| `library.*` | livres et utilisateurs, règles d'emprunt et de suppression |
| `book.*`, `user.*` | modèles et sérialisation au format `|` |
| `filemanager.*` | chargement, sauvegarde atomique et backup |
| `bindings.cpp` | interface pybind11 : `Book`, `User`, `Library`, `FileManager`, `LibraryError` |
| `GUI/data_store.py` | adaptateur mince : validation des saisies, délégation au moteur, `StoreError` |
| `GUI/app.py` | fenêtre, bandeau et navigation |
| `GUI/views.py` | pages Livres et Utilisateurs, pied de page commun |
| `GUI/panels.py` | panneaux latéraux des formulaires |
| `GUI/theme.py` | palette, polices et styles |

`data_store.py` ne tient ni état ni persistance : doublons, identifiants
`USRXXX` et règles d'emprunt restent dans `library.cpp`.

## Formats des données

- `books.txt` : `titre|auteur|isbn|1ou0|idEmprunteur`
- `users.txt` : `nom|id|isbn1,isbn2` — troisième champ vide (ligne terminée par
  `|`) quand l'utilisateur n'a aucun emprunt.

Dans la GUI, les champs saisis ne peuvent pas contenir `|` ; la CLI, elle,
n'applique pas cette validation et un `|` saisi casserait le format. `data/`
contient des données réelles : pour tout essai destructif, travailler sur une
copie.

## Tests

Il n'y a ni suite automatisée ni CI. La compilation avec `-Wall -Wextra
-Wpedantic` et les vérifications manuelles des deux clients servent de contrôle ;
les scripts de vérification ponctuels restent hors du dépôt.

## Artefacts ignorés

`build/`, `GUI/.venv/`, `GUI/__pycache__/`, `GUI/*.so`, `data/*.tmp` et
`data/*.backup` sont générés localement et ne sont pas versionnés.
