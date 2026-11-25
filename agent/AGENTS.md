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
- `data_store.py` est un adaptateur mince : il valide et met en forme les
  saisies, puis délègue au moteur C++ via `bibliotheque_core` (voir « Liaison
  pybind11 avec le moteur C++ »). Il ne tient plus ni état ni persistance.
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
  `Créer sauvegarde` restent à brancher (étape distincte, après la
  documentation). Mettre cette section à jour à chaque évolution de l'UI.
- Formulaire d'ajout d'utilisateur : le champ ID du prototype est remplacé par la
  génération automatique `USRXXX`. Nom obligatoire, sans chiffres, avec majuscule
  en début de mot et après un tiret (pas après une apostrophe).

### Liaison pybind11 avec le moteur C++

Intégration suivie étape par étape ; mettre à jour les cases et la ligne d'état
après chaque étape, sans y consigner la conversation.

- [x] 1. Build : `bibliotheque_lib`, option `BUILD_PYTHON_BINDINGS`, module
  `bibliotheque_core` généré dans `GUI/`, import vérifié.
- [x] 2. `bindings.cpp` : `Book`, `User`, `Library`, `FileManager`, copies
  `books()` / `users()`, `remove_user`, nettoyage dans `remove_book`.
- [x] 3. Persistance C++ : sauvegarde atomique et backup écrasable.
- [x] 4. Adaptateur `data_store.py` : API conservée, module obligatoire,
  validation des saisies et délégation au moteur C++.
- [x] 5. UI : rollback de `panels.py` via `remove_user`.
- [x] 6. Vérifications : parité, CRUD, emprunt/retour, rollback, backup,
  régression CLI et tests UI.
- [ ] 7. Documentation : commandes de build et architecture à jour.

**État d'avancement :** étapes 1 à 6 terminées, étape 7 à faire.
**Dernière vérification :** étape 6 sur copies (`/tmp/opencode/etape6/`), base
réelle 40/27/13/27 (40 livres, 27 disponibles, 13 empruntés, 27 utilisateurs).
40 contrôles : 24 moteur (parité aller-retour octet pour octet, CRUD,
emprunt/retour, rollback, atomicité des deux fichiers, backup via
`LibraryStore.create_backup()` et restauration), 8 CLI (scénario complet,
relance, mode mémoire, parité croisée) et 8 UI (cartes et pied de page, ajout
`USR028`, refus, rollback, ouverture du panneau avec un grab étranger réel).
`data/` inchangé (sha256), aucun `.tmp` ni `.backup` résiduel.

### Reprise

Point d'entrée d'une nouvelle session : lire cette section puis attaquer l'étape 7
(documentation). Ne rien recommencer des étapes 1 à 6.

- Build avec le module Python : les chemins du venv et de pybind11 sont explicites.
  Depuis `agent/` :
  `cmake -S . -B build -DBUILD_PYTHON_BINDINGS=ON
  -DPython_EXECUTABLE="$PWD/GUI/.venv/bin/python"
  -Dpybind11_DIR=/usr/lib/cmake/pybind11` puis `cmake --build build -j`.
- Contrôle de l'étape 1 : `cd GUI && .venv/bin/python -c
  "import bibliotheque_core as b; print(b.__version__)"` doit afficher `0.1.0`.
- `bindings.cpp` expose `Book`, `User`, `Library` et `FileManager` ; `books()` et
  `users()` renvoient des copies, `find_book` / `find_user` renvoient `None` si
  l'élément est absent. Les propriétés de `Book` et `User` sont en lecture seule.
- `remove_user` refuse la suppression d'un utilisateur qui a encore des
  emprunts en cours.
- Le module expose `create_book`, `create_user`, `search_books`,
  `check_out_book_checked` et `return_book_checked` ; les refus métier lèvent
  `LibraryError`, traduite en `StoreError` par `data_store.py`.
- `data_store.py` ne tient plus l'état : `LibraryStore` enveloppe `core.Library`
  et `core.FileManager`. Les validations Python se limitent au trim, au refus du
  vide et de `|`, et à la mise en forme du nom ; doublons, identifiants et règles
  d'emprunt restent dans `library.cpp`.
- Persistance C++ : chaque fichier est écrit dans `<fichier>.tmp` puis renommé
  sur sa cible (remplacement atomique) ; `books.txt` et `users.txt` sont préparés
  tous les deux avant les renommages. `createBackup()` écrase `<fichier>.backup`
  de la même façon et renvoie `bool`. Pas de `fsync` : l'atomicité protège des
  erreurs d'écriture, pas d'une coupure de courant.
- Le `.so` est produit dans `GUI/` et ignoré par Git ; ne jamais le commiter.
- Ne jamais ajouter `-isystem /usr/include` aux options de compilation : GCC
  casse alors sa chaîne d'inclusion (`#include_next <stdlib.h>`). Les chemins
  d'IntelliSense passent uniquement par les `c_cpp_properties.json`.
- `data/books.txt` et `data/users.txt` sont des données réelles : aucun essai
  destructif dessus, toujours travailler sur une copie (`/tmp/opencode/...`).
- Aucun repli Python prévu : si `bibliotheque_core` manque, la GUI doit échouer
  clairement plutôt que revenir à la persistance Python.
- `LibraryStore` expose `create_backup()` : délégation à
  `FileManager::createBackup()`, `False` s'il n'y a aucun fichier à sauvegarder,
  `OSError` si la copie échoue.
- Actions GUI encore inertes (`Livre +`, recherche, filtre, emprunt, retour,
  suppression, `Créer sauvegarde`) : étape distincte, après la documentation.
- `SidePanel.show()` ignore un `grab failed` (grab détenu par un autre client X) :
  le panneau s'ouvre et reste utilisable, simplement non modal. Vérifié avec un
  client X qui détient réellement le grab.

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
