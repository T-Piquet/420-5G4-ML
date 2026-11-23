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
  `agent/build/bibliotheque -d agent/data/`.
- Sans `-d`, mode mémoire explicite : message au démarrage, aucun chargement,
  commandes 12 (sauvegarder) et 13 (backup) ignorées avec un message, aucune
  sauvegarde à la sortie et aucun fichier créé.
- `build/*` est gitignoré : ne jamais commiter les artefacts de build.
- Aucun test, linter ni CI : la seule vérification est la compilation avec
  `-Wall -Wextra -Wpedantic` (déjà dans CMake).

## Architecture
- `main.cpp` : point d'entrée et menu CLI.
- `Library` (`library.*`) possède les `Book` et `User` via `unique_ptr`.
- `FileManager` (`filemanager.*`) gère la persistance ; `hasPersistence()` distingue
  le mode mémoire (sans `-d`) du mode fichier ; `book.*` et `user.*` portent la
  sérialisation.
- C++17, extensions désactivées ; `using namespace std;` est utilisé partout dans le code existant.

## Format des données (`data/`)
- `books.txt` : `titre|auteur|isbn|1ou0|idEmprunteur` (séparateur `|`).
- `users.txt` : `nom|id|isbn1,isbn2` (3e champ séparé par des virgules).
- Modifier ces formats casse le parsing de `FileManager` et les fichiers de test fournis.

## Devcontainer
- Config dans `agent/.devcontainer` : monte le X11 de l'hôte (`DISPLAY`, `--net=host`)
  pour le futur GUI. Ouvrir `agent/` comme dossier du conteneur.
- `.vscode/settings.json` (racine) pointe vers `${workspaceFolder}/agent`. Les
  fichiers `.vscode/c_cpp_properties.json` (racine et `agent/`) donnent à IntelliSense
  les chemins `/usr/include` et `/usr/include/python3.13` ; `compile_commands.json`
  reste généré pour les autres outils.

## GUI Python (`GUI/`)
- Application CustomTkinter à fenêtre unique ; elle lit/écrit les mêmes
  `data/books.txt` et `data/users.txt` que la CLI (formats ci-dessus).
- Venv local :
  `cd agent/GUI && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- Lancement : `.venv/bin/python app.py` ; option `--data-dir` (défaut : `agent/data`).
- `data_store.py` isole encore la persistance Python ; le moteur C++ sera branché
  via pybind11 (voir « Liaison pybind11 avec le moteur C++ »). Il faut garder ce
  module compatible avec les formats de fichiers du C++.
- `app.py` crée la fenêtre et gère la navigation entre les pages ; `views.py`
  contient les pages et le pied de page commun, `panels.py` les panneaux latéraux
  des formulaires et `theme.py` centralise l'apparence.
- `GUI/.venv/` et `__pycache__/` sont ignorés par `GUI/.gitignore`.
- Version de test actuelle : un bandeau « Gestionnaire de la Bibliothèque » coiffe
  la page Livres, écran principal, avec ses cartes sur trois colonnes (titre,
  auteur, ISBN, actions inertes), la barre de recherche et le filtre `Tous` /
  `Disponibles` / `Empruntés`. `Voir utilisateurs` ouvre la page Utilisateurs en
  lecture seule (cartes sur quatre colonnes, statistiques réelles en pied de page) ;
  son bouton `Utilisateur +` ouvre un panneau latéral fonctionnel : validation et
  mise en forme du nom, identifiant `USRXXX` généré, messages et rafraîchissement
  immédiat. `Voir livres` ramène à l'écran Livres. `Livre +`, la recherche, le
  filtre, l'ajout de livre, l'emprunt, le retour, la suppression et
  `Créer sauvegarde` restent à brancher. Mettre cette section à jour à chaque
  évolution de l'UI.
- Formulaire d'ajout d'utilisateur : le champ ID du prototype est remplacé par la
  génération automatique `USRXXX`. Nom obligatoire, sans chiffres, avec majuscule
  en début de mot et après un tiret (pas après une apostrophe).

### Liaison pybind11 avec le moteur C++

Intégration suivie étape par étape ; mettre à jour les cases et la ligne d'état
après chaque étape, sans y consigner la conversation.

- [x] 1. Build : `bibliotheque_lib`, option `BUILD_PYTHON_BINDINGS`, module
  `bibliotheque_core` généré dans `GUI/`, import vérifié.
- [ ] 2. `bindings.cpp` : `Book`, `User`, `Library`, `FileManager`, copies
  `books()` / `users()`, `remove_user`, nettoyage dans `remove_book`.
- [ ] 3. Persistance C++ : sauvegarde atomique et backup écrasable.
- [ ] 4. Adaptateur `data_store.py` : API conservée, module obligatoire,
  pré-validation des lignes.
- [ ] 5. UI : rollback de `panels.py` via `remove_user`.
- [ ] 6. Vérifications : parité, CRUD, emprunt/retour, rollback, backup,
  régression CLI et tests UI.
- [ ] 7. Documentation : commandes de build et architecture à jour.

**État d'avancement :** étape 1 terminée, étape 2 à faire.
**Dernière vérification :** module `bibliotheque_core` importé (version 0.1.0),
CLI recompilée et statistiques 39/26/13/27 lues sur une copie des données.

### Thème et apparence
- Source unique : `GUI/theme.py` (palette, polices, styles). Aucune couleur ne doit
  être codée en dur dans les vues.
- Typographie : Garamond est la police voulue, mais elle n'est pas installée dans
  le conteneur ; `theme.py` résout la première famille disponible :
  `Garamond` → `EB Garamond` → `DejaVu Serif`. La substitution doit rester
  transparente pour le reste du code.
- Palette beiges et verts muets :
  fond `#F4EFE4`, surface `#EAE3D2`, survol `#DFD6C1`, vert sauge `#6E7F5F`,
  vert survol `#5B6A4E`, vert doux `#A9B49B`, terracotta `#A4705A`,
  texte `#33352C`, texte secondaire `#6C6E62`.
- Aucun contour : `border_width=0` partout, pas de séparateur ni de cadre
  visible ; les zones se distinguent uniquement par leur `fg_color`.
- Arrondis discrets : `corner_radius=6`.
- Pas de mode sombre : le thème beige/vert est unique.
- Chaque page est surmontée d'un bandeau pleine largeur « Gestionnaire de la
  Bibliothèque », sur fond surface (`#EAE3D2`), texte centré en gras.
- Icônes dessinées au Canvas (corbeille en terracotta) plutôt qu'en emojis,
  pour éviter le rendu couleur et les dépendances d'image.
- Les formulaires utilisent un panneau latéral (voir « Formulaires ») ; les
  confirmations restent des modales centrées. Ne pas utiliser `messagebox` natif.
- Barres de défilement stylées avec les couleurs du thème, sinon elles
  réintroduisent des gris et des contours.

### Formulaires
- Modèle unique : panneau latéral droit (`SidePanel` dans `GUI/panels.py`),
  `CTkToplevel` sans décoration, largeur 400 px, aligné sous le bandeau et sur
  toute la hauteur restante.
- `transient` + `grab_set` pour bloquer la page ; fermeture par `Annuler` ou
  `Échap`, avec libération du grab avant destruction.
- Contenu : titre en haut, champs et aide au centre, boutons et zone de message
  en bas. Un nouveau formulaire hérite de `SidePanel` et redéfinit `_build_form`.
- Soumission : validation via `LibraryStore`, sauvegarde, message dans le panneau
  puis rafraîchissement de la vue ; en cas d'échec d'écriture, l'ajout en mémoire
  est annulé. Après un ajout réussi, le panneau reste ouvert et le champ est vidé.

## Conventions
- Code, commentaires, chaînes d'interface et messages de commit en français.
- Préfixes de commit : `[FEAT]`, `[TACHE]`, `[DOCS]`, `[REMISE]`, `[SAUVEGARDE]`.
- Notes de travail : `agent/notes-instructions-projet-llm-agent.md` — avancer une étape
  à la fois (alternance plan/build), exécuter le code avant de commiter.
- Ce fichier est versionné ; ce n'est pas un journal de conversation.
