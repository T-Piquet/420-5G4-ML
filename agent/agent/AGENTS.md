# AGENTS.md

`bibliotheque` est une application CLI C++17 (interface en français) de gestion de bibliothèque. C'est la 3e partie d'un atelier : les parties Python sont dans `apprentissage/` et `analyse_image/` à la racine, hors du périmètre de ce dossier.

## Compilation
- Depuis `agent/` : `cmake -S . -B build && cmake --build build`
- `CMakeLists.txt` liste explicitement les sources du noyau (`book.cpp`, `user.cpp`, `library.cpp`, `filemanager.cpp`), vise C++17 avec `-Wall -Wextra -Wpedantic`. Ajouter un `.cpp` implique de l'ajouter aux deux cibles : il n'y a plus de glob.
- Deux cibles : l'exécutable `bibliotheque` et le module Python `bibliotheque_py` (construit si pybind11 est trouvé ; option `BUILD_PYTHON_BINDINGS`, défaut ON).
- Aucun test, linter, formatteur ni CI : compiler puis lancer `python/example.py` sont les seules vérifications.

## Exécution
- Toujours passer un dossier de données : `./build/bibliotheque -d agent/data` depuis la racine, ou `./bibliotheque -d data` depuis `agent/`.
- Sans `-d` / `--data-dir`, les noms de fichiers sont vides : le chargement ne trouve rien et la sauvegarde échoue avec un message d'erreur.
- Application interactive (menu) qui lit/écrit `books.txt` et `users.txt` : `titre|auteur|isbn|1|0|idEmprunteur` et `nom|id|isbn1,isbn2,...` (voir `book.cpp` / `user.cpp`).
- Les fichiers `data/books.txt` et `data/users.txt` sont suivis par git et **réécrits à la sortie** (menu 0) et au menu 12 : copier `data/` avant un test manuel pour ne pas salir l'arbre de travail. Le menu 13 crée des fichiers `.backup` à côté des originaux.

## Interface Python
- Le module compilé est copié automatiquement dans `python/` (commande POST_BUILD du CMake) : `python3 python/example.py` depuis `agent/`, sans `PYTHONPATH`. L'artefact (`*.so` / `*.pyd`) est ignoré par git.
- API en snake_case : `Book`, `User`, `Library`, `FileManager` (voir `python_bindings.cpp`).
- `Library` possède ses objets via `unique_ptr` : les retours de pointeurs utilisent `py::return_value_policy::reference_internal`. Ne pas passer en `take_ownership` (double delete) ni en `reference` (pointeur pendant).
- `python/example.py` copie `data/` dans un dossier temporaire ; ne pas lancer la CLI directement sur `data/`.
- `python/gui.py` : interface tkinter en deux couches — `LibraryController` (logique pure, retourne des dicts) et `BibliothequeApp` (vue Tk). Garder les objets pybind11 dans le contrôleur, pas dans les widgets.
- Dans cet environnement d'agent, `DISPLAY` est vide et Xvfb est absent : ne pas tenter d'ouvrir la fenêtre ; vérifier avec `python3 -m py_compile python/gui.py` et `python3 python/gui.py --selftest`.
- `gui.py` importe `bibliotheque_py as bp` (module copié dans `python/`) : ne pas réintroduire de chemin vers `build/` ni d'import `bibliotheque_python`.
- Depuis un hôte Windows, garder l'exécution dans le Dev Container : `.devcontainer/devcontainer.json` fixe `DISPLAY=host.docker.internal:0.0` pour un serveur X Windows (VcXsrv, « Disable access control »). Le mount de `/tmp/.X11-unix` reste commenté (chemin Linux inexistant sur Windows). Après « Rebuild Container », reconstruire et lancer `python3 python/gui.py`.
- Build Windows natif reste possible en option via `python/build_windows.bat` (MSVC, architecture détectée depuis Python, `pybind11_DIR` issu de `python -m pybind11 --cmakedir`, build `--config Release`). Le `.pyd` porte l'ABI du Python utilisé, donc compiler et lancer avec le même Python. `python/lancer_gui.bat` ouvre `gui.py` au double-clic.

## Devcontainer
- Les lignes `mounts`, `containerEnv.DISPLAY` et `runArgs` de `.devcontainer/devcontainer.json` sont commentées malgré ce qu'annonce `README.md` ; les décommenter pour l'affichage X11.
- Le Dockerfile installe CMake 3.22.2, opencode et ollama ; `CMakeLists.txt` exige CMake >= 3.21.

## Conventions et pièges
- Interface, messages et commentaires en français : garder le français pour tout nouveau texte visible par l'utilisateur.
- `.vscode/settings.json` à la racine contient un `cmake.sourceDirectory` Windows codé en dur (chemin de l'auteur) : l'ignorer, la source est `agent/`.
- Les fichiers suivis sont en CRLF dans ce checkout alors que l'index git est en LF : `git diff` peut afficher des fichiers entiers modifiés sans vrai changement. Ne pas « corriger » les fins de ligne par accident.
