# AGENTS.md

## Portée

Ce dossier contient l'application C++ `bibliotheque` et son interface graphique Python CustomTkinter. Les notebooks Python des dossiers parents `apprentissage/` et `analyse_image/` ne concernent pas ce périmètre. Conserver les textes affichés, messages et commentaires en français.

## Compiler et exécuter

Depuis `agent/` :

```bash
cmake -S . -B build
cmake --build build -j
./build/bibliotheque -d data
```

- Toujours fournir `-d` ou `--data-dir` : sans cette option, les chemins de fichiers sont vides et la sauvegarde échoue.
- Le répertoire passé à `-d` doit contenir `books.txt` et `users.txt`.
- L'application C++ est interactive et terminal-only. Le choix `0` sauvegarde puis quitte ; le choix `13` crée ou écrase les fichiers `.backup`.
- Pour un test sans modifier les données suivies, copier `data/` dans un répertoire temporaire et lancer avec `-d <temporaire>`.
- Il n'y a ni tests, ni linter, ni CI. Vérifier une modification par la compilation, puis par une exécution avec des données temporaires.

## Build

- `CMakeLists.txt` globbe `*.cpp` : relancer CMake après ajout ou suppression d'un fichier source.
- Le projet exige CMake >= 3.21 et compile en C++17 avec `-Wall -Wextra -Wpedantic`.
- Le binaire produit est `build/bibliotheque` ; `build/*` est ignoré par `agent/.gitignore`.
- Le devcontainer `agent/.devcontainer` installe CMake 3.22.2. Son montage X11 est inutile pour cette application en terminal.

## Bindings Python

- `bibliotheque_bindings.cpp` expose `Book`, `User`, `Library` et `FileManager`.
- La cible `bibliotheque_python` n'est créée que si `pybind11` est trouvé (`find_package(pybind11 CONFIG)`), sinon CMake l'ignore avec un message.
- Le repli CMake accepte aussi une installation pip de pybind11 via `python3 -m pybind11 --cmakedir` ; activer le venv avant de configurer si nécessaire.
- Le venv local `agent/.venv` (ignoré par Git) sert à pybind11 ; le recréer avec `python3 -m venv .venv && .venv/bin/pip install pybind11` puis activer `.venv` avant CMake.
- Une compilation avec pybind11 produit `build/bibliotheque.cpython-*.so` ; l'import se fait avec `PYTHONPATH=build python3 -c 'import bibliotheque'`.
- La cible Python liste ses sources explicitement : ajouter tout nouveau `.cpp` métier à `bibliotheque_python`.

## Interface graphique CustomTkinter

- Le paquet `interface/` construit l'interface à partir du module pybind11 : `.venv/bin/python -m interface -d data` depuis `agent/`.
- Installer la dépendance avec `.venv/bin/pip install -r requirements.txt` (CustomTkinter).
- L'interface cherche automatiquement le module compilé dans `build/` ; compiler d'abord le projet.
- Les écrans Livres, Utilisateurs et Paramètres sont complets.
- L'écran Utilisateurs permet l'ajout ; la suppression d'un utilisateur n'est pas proposée. Les cartes affichent le nombre de livres empruntés et leurs ISBN.
- L'écran Paramètres propose « Sauvegarder les données », « Créer une sauvegarde » et « Statistiques de la bibliothèque ». La création de sauvegarde enregistre d'abord les données puis écrase `books.txt.backup` et `users.txt.backup`.
- Les modifications restent en mémoire et ne sont écrites qu'à la fermeture de la fenêtre ou via « Sauvegarder les données ».
- Recherche et filtre sont appliqués côté Python, sans tenir compte des accents ; la suppression d'un livre emprunté est bloquée.
- La barre de navigation souligne l'onglet actif.
- Les cartes de livres et d'utilisateurs utilisent des widgets Tk standards pour rester fluides ; ne pas les remplacer par des `CTkLabel`/`CTkFrame` sans mesurer le coût de rendu.
- Pour tester sans risque, copier `data/` dans un répertoire temporaire et lancer l'interface avec `-d <temporaire>`.

## Format des données

Les champs sont séparés sans échappement ; ne pas introduire le séparateur dans une valeur.

- `books.txt` : `titre|auteur|isbn|1-ou-0|idEmprunteur`
- `users.txt` : `nom|id|isbn1,isbn2`

Les données sont chargées au démarrage et sauvegardées via le menu `12` ou à la sortie avec `0` pour l'application C++, à la fermeture ou via Paramètres pour l'interface graphique.
