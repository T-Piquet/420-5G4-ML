# AGENTS.md — agent/

Projet C++17 « bibliotheque » : gestion de bibliothèque en CLI.
Tout le travail et la documentation de cette partie restent dans `agent/`.

## Build et exécution
- Build : `cd agent && cmake -S . -B build && cmake --build build`
  (équivalent au `mkdir build && cd build && cmake .. && make` du README).
- `CMakeLists.txt` fait un glob de `*.cpp` : ajouter un fichier source impose de
  relancer cmake, pas seulement `make`.
- Exécution depuis `agent/build` : `./bibliotheque -d ../data/`.
  Le chemin est résolu par rapport au CWD ; depuis la racine du dépôt :
  `agent/build/bibliotheque -d agent/data/`. Sans `-d`, rien n'est chargé ni sauvegardé.
- `build/*` est gitignoré : ne jamais commiter les artefacts de build.
- Aucun test, linter ni CI : la seule vérification est la compilation avec
  `-Wall -Wextra -Wpedantic` (déjà dans CMake).

## Architecture
- `main.cpp` : point d'entrée et menu CLI.
- `Library` (`library.*`) possède les `Book` et `User` via `unique_ptr`.
- `FileManager` (`filemanager.*`) gère la persistance ; `book.*` et `user.*` portent
  la sérialisation.
- C++17, extensions désactivées ; `using namespace std;` est utilisé partout dans le code existant.

## Format des données (`data/`)
- `books.txt` : `titre|auteur|isbn|1ou0|idEmprunteur` (séparateur `|`).
- `users.txt` : `nom|id|isbn1,isbn2` (3e champ séparé par des virgules).
- Modifier ces formats casse le parsing de `FileManager` et les fichiers de test fournis.

## Devcontainer
- Config dans `agent/.devcontainer` : monte le X11 de l'hôte (`DISPLAY`, `--net=host`)
  pour le futur GUI. Ouvrir `agent/` comme dossier du conteneur.
- `.vscode/settings.json` (racine) contient un chemin absolu obsolète (`/home/cano/repos/...`) :
  utiliser la CLI plutôt que CMake Tools.

## Conventions
- Code, commentaires, chaînes d'interface et messages de commit en français.
- Préfixes de commit : `[FEAT]`, `[TACHE]`, `[DOCS]`, `[REMISE]`, `[SAUVEGARDE]`.
- Notes de travail : `agent/notes-instructions-projet-llm-agent.md` — avancer une étape
  à la fois (alternance plan/build), exécuter le code avant de commiter.
- Ce fichier est versionné ; ce n'est pas un journal de conversation.
