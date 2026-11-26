# AGENTS.md (agent/)

Application console C++17 "bibliotheque" (gestion de livres/utilisateurs).
Pas de tests, lint, formatter ni CI dans ce dossier.

## Compilation
Depuis `agent/` :
```
mkdir -p build && cd build
cmake .. && make
```
- Binaire : `agent/build/bibliotheque`. `build/` est gitignoré, ne pas committer.
- `CMakeLists.txt` utilise `file(GLOB "*.cpp")` : après ajout/suppression d'un `.cpp`,
  relancer `cmake ..` (un simple `make` ne le détecte pas).
- Flags : `-Wall -Wextra -Wpedantic`, C++17 strict (`CXX_EXTENSIONS NO`).

## Exécution
Toujours passer le dossier de données, sinon rien n'est chargé/sauvegardé
(noms de fichiers vides) :
```
./bibliotheque -d ../data        # depuis build/
```
Options acceptées : `-d <dir>` ou `--data-dir <dir>`.
Fichiers d'exemple : `agent/data/books.txt` et `agent/data/users.txt`.

## Format de stockage (pipe-séparé, à préserver)
- livres : `titre|auteur|isbn|1ou0|borrowerId`
- utilisateurs : `nom|userId|isbn1,isbn2,...`
La sauvegarde se fait au menu 12 et à la sortie (choix 0).

## Conventions
- Garder l'UI, les messages et les commentaires en français.
- Code : `main.cpp` (menu CLI) ; `Library` possède des `unique_ptr<Book/User>` ;
  `FileManager` gère la sérialisation ; `Book`/`User` portent le format fichier.
- Devcontainer fourni dans `.devcontainer/` (C++ + CMake + redirection X11).
