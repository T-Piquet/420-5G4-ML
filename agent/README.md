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

Le module `bibliotheque_py` expose `Book`, `User`, `Library` et `FileManager` avec des noms en snake_case. Il est construit en même temps que l'exécutable si pybind11 est disponible (`pybind11-dev` ou `pip install pybind11`) ; sinon seule la CLI est compilée.

Depuis `agent/` :

```
cmake -S . -B build
cmake --build build
python3 python/example.py
```

La compilation copie automatiquement le module dans `python/`, à côté de `gui.py` : aucun `PYTHONPATH` n'est nécessaire. `python/example.py` copie `data/` dans un dossier temporaire : les fichiers suivis par git ne sont pas modifiés.

# Interface graphique

`python/gui.py` est une interface tkinter (bibliothèque standard, déjà présente dans le devcontainer) branchée sur `bibliotheque_py` : ajout/suppression et recherche de livres, gestion des utilisateurs, emprunts/retours, sauvegarde.

```
python3 python/gui.py
python3 python/gui.py --data-dir /chemin/vers/data
python3 python/gui.py --selftest
```

L'interface s'ouvre sur `agent/data/` et avertit que la sauvegarde réécrit ces fichiers suivis par git. `--selftest` vérifie la logique sans ouvrir de fenêtre. La configuration X11 pour un hôte Windows est décrite ci-dessous.

## Affichage sur Windows depuis le Dev Container

L'interface et le module Python (`.so`) restent dans le conteneur Linux ; seule la fenêtre tk est affichée sur Windows via un serveur X.

1. Sur Windows, installer **VcXsrv** https://github.com/marchaesen/vcxsrv/releases. Le lancer avec `Multiple windows` → `Start no client` et cocher **Disable access control** : le conteneur se connecte depuis une autre IP. Autoriser VcXsrv dans le pare-feu Windows.
2. `.devcontainer/devcontainer.json` est déjà configuré :

   ```jsonc
   "containerEnv": {
     "DISPLAY": "host.docker.internal:0.0"
   }
   ```

   Le mount de `/tmp/.X11-unix` reste commenté : ce chemin n'existe pas sur un hôte Windows. Docker Desktop résout `host.docker.internal` ; si nécessaire, ajouter `"runArgs": ["--add-host=host.docker.internal:host-gateway"]`.
3. Dans VS Code : **Dev Containers: Rebuild Container**, puis dans le terminal du conteneur :

   ```bash
   echo $DISPLAY                 # host.docker.internal:0.0
   cmake -S . -B build && cmake --build build
   python3 python/gui.py --selftest
   python3 python/gui.py
   ```

   La compilation copie le module dans `python/` : aucun `PYTHONPATH` n'est nécessaire.

Si la fenêtre ne s'ouvre pas : vérifier que VcXsrv est lancé, que **Disable access control** est coché et que le pare-feu autorise la connexion.

## Build Windows natif (optionnel)

Si vous préférez exécuter l'interface directement sur Windows, `python\build_windows.bat` compile le `.pyd` avec MSVC (Python depuis python.org avec tkinter, Visual Studio Build Tools « Développement desktop avec C++ », `pip install pybind11`) puis lance le `--selftest`. Le `.pyd` est lié à la version et à l'architecture du Python utilisé (`cp313-win_amd64` par exemple) : compiler et lancer avec le même Python. Le `.so` Linux ne fonctionne pas sur Windows.