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
  auteur, ISBN, action et corbeille), la recherche et le filtre `Tous` /
  `Disponibles`. La recherche n'applique le texte qu'au clic sur la
  loupe : elle parcourt les titres et les auteurs (sous-chaîne, casse ASCII
  ignorée) et ne laisse que les cartes correspondantes ; une requête vide ramène
  tout, une requête sans résultat affiche un message avec la saisie. La touche
  `Entrée` ne réaffiche toutes les cartes que si le champ est vide ; avec du
  texte, elle ne lance rien. Le filtre s'applique immédiatement, se combine avec
  la recherche et ne propose que `Tous` ou les livres disponibles (pas de filtre
  « Empruntés ») ; `Entrée` sur champ vide conserve le filtre courant.
  `Voir utilisateurs` ouvre la page Utilisateurs en lecture seule (cartes sur
  quatre colonnes, statistiques réelles en pied de page) ;
  son bouton `Utilisateur +` ouvre un panneau latéral fonctionnel : validation et
  mise en forme du nom, identifiant `USRXXX` généré, messages et rafraîchissement
  immédiat. `Voir livres` ramène à l'écran Livres. `Créer sauvegarde`, dans le
  pied de page commun, copie les deux fichiers via `LibraryStore.create_backup()`
  et affiche un message discret à côté des boutons (« Sauvegarde créée. »,
  « Aucun fichier à sauvegarder. », échec en terracotta). Sur une carte
  disponible, `Emprunter` ouvre un panneau latéral de choix de l'emprunteur
  (menu `Nom (USRXXX)`, 28 utilisateurs) : la validation appelle
  `LibraryStore.checkout()` puis sauvegarde, ferme le panneau et met à jour les
  cartes, les statistiques et le message du pied de page ; en cas d'échec
  d'écriture, l'emprunt est annulé en mémoire. Sur une carte empruntée,
  `Retourner` rend le livre disponible, sauvegarde, met à jour cartes,
  statistiques et message du pied de page ; en cas d'échec d'écriture, l'emprunt
  est remis en place. La corbeille d'une carte supprime le livre immédiatement,
  sans confirmation : le moteur retire aussi l'ISBN des listes d'emprunt, puis
  cartes, statistiques et message du pied de page sont mis à jour ; en cas
  d'échec d'écriture, l'état est relu depuis le disque. `Livre +` ouvre un
  panneau latéral (titre, auteur, ISBN) : l'ajout passe par
  `LibraryStore.add_book()`, sauvegarde, vide les champs et met à jour la
  grille et les statistiques ; en cas d'échec d'écriture, le livre est retiré
  en mémoire. Toutes les actions de l'écran Livres sont branchées. Mettre cette
  section à jour à chaque évolution de l'UI.
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
- [x] 7. Documentation : commandes de build et architecture à jour.
- [x] 8. Première action GUI branchée : `Créer sauvegarde` du pied de page
  appelle `LibraryStore.create_backup()`, avec message de retour.
- [x] 9. Recherche branchée : clic sur la loupe, texte appliqué à ce moment-là,
  titres et auteurs via `LibraryStore.search()`, cartes filtrées et message si
  aucun résultat.
- [x] 10. Filtre branché : menu `Tous` / `Disponibles`, `available_books` exposé
  dans `bindings.cpp`, combinaison avec la recherche via
  `LibraryStore.filter_books()`.
- [x] 11. Emprunt branché : `BorrowPanel` (choix de l'emprunteur), appel à
  `LibraryStore.checkout()` puis `save()`, rollback en cas d'échec d'écriture,
  rafraîchissement des cartes, des statistiques et message du pied de page.
- [x] 12. Retour branché : `Retourner` appelle `LibraryStore.return_book()` puis
  `save()`, rollback par `checkout()` en cas d'échec d'écriture, message du pied
  de page avec l'emprunteur.
- [x] 13. Suppression branchée : clic sur la corbeille, `LibraryStore.remove_book()`
  puis `save()` sans confirmation, restauration par `load()` en cas d'échec
  d'écriture, message du pied de page.
- [x] 14. Ajout de livre branché : `Livre +` ouvre `AddBookPanel`, appel à
  `LibraryStore.add_book()` puis `save()`, rollback par `remove_book()` en cas
  d'échec d'écriture, champs vidés et messages dans le panneau.

**État d'avancement :** étapes 1 à 14 terminées ; toutes les actions GUI sont
branchées.
**Dernière vérification :** étape 14 sur copies (`/tmp/opencode/etape14/`), base
réelle 39/25/14/28 (39 livres, 25 disponibles, 14 empruntés, 28 utilisateurs ;
`O Llama|USR028` ajouté, deux emprunts de `USR013` et un livre supprimé depuis la
GUI). 12 contrôles ajout : champs nettoyés et livre disponible, statistiques
livres/disponibles +1, utilisateurs inchangés, rechargement depuis les fichiers,
ISBN dupliqué refusé, champs vides et `|` refusés, panneau ouvert par
`Livre +`, ajout complet (carte, statistiques, message, champs vidés, fichier),
doublon et titre vide sans ajout, échec de `save` avec ajout annulé et fichiers
intacts, nouvelle soumission après l'échec, visibilité sous `Disponibles`.
Rappels : 24 moteur, 8 CLI, 8 UI, 6 sauvegarde, 13 recherche, 13 filtre,
11 emprunt, 10 retour, 9 suppression, soit 114 contrôles. Étape 7 :
`agent/README.md` réécrit (deux clients, build pybind11, GUI, architecture et
formats) ; build documenté rejoué dans `/tmp/opencode/build-doc`. Rebuild étape
10 effectué avec `BUILD_PYTHON_BINDINGS=ON` ; module `0.1.0`. Les étapes 11 à 14
ne touchent pas au C++ : pas de rebuild.
`agent/data` n'a pas été modifié par les tests (hors ajout, emprunts et
suppression de l'utilisateur) ; aucun `.tmp` ni `.backup` résiduel.

### Reprise

Point d'entrée d'une nouvelle session : lire cette section puis attaquer le
branchement des actions GUI. Ne rien recommencer des étapes 1 à 14.

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
- `Créer sauvegarde` est branchée dans `PageFooter` : `invoke()` appelle
  `LibraryStore.create_backup()`, puis affiche « Sauvegarde créée. » (sage),
  « Aucun fichier à sauvegarder. » (discret) ou l'erreur (terracotta). Le message
  est remis à zéro à chaque changement de page ; le bouton existe sur les deux
  pages.
- Recherche branchée dans `BooksView` : `search_icon.bind("<Button-1>")` appelle
  `_apply_search()`, qui lit `search_entry.get().strip()` et passe la requête à
  `LibraryStore.search()` (moteur C++ `searchBooks` : titre **ou** auteur,
  sous-chaîne, casse ASCII). `_populate_cards(liste)` ne reçoit que les cartes
  concernées ; une liste vide affiche un message reprenant la requête.
  La saisie seule ne déclenche rien ; `Entrée` réaffiche toutes les cartes
  uniquement quand le champ est vide (`_on_search_return`), sinon elle ne fait
  rien. Le pied de page reste global. Limite :
  `toLower()` est ASCII, donc `etranger` ne trouve pas « L'Étranger ».
- Filtre branché dans `BooksView` : le menu ne propose que `Tous` et
  `Disponibles` ; `_on_filter_change()` met à jour `_active_filter` (`all` /
  `available`) et appelle `_refresh_cards()`, qui interroge
  `LibraryStore.filter_books(query, availability)`. Sans requête, l'adaptateur
  renvoie directement `books` ou `available_books` (C++ `getAvailableBooks`,
  exposé dans `bindings.cpp`) ; avec requête, il croise `search_books` et les
  ISBN disponibles. Le filtre se combine donc avec la recherche et `Entrée` sur
  champ vide le conserve. Messages : requête sans résultat, puis
  « Aucun livre dans ce filtre. » si le filtre seul est vide. Le pied de page
  reste global ; revenir sur la page réinitialise le menu à `Tous`.
- Emprunt branché : `BookCard` reçoit `on_borrow` pour les livres disponibles.
  Le clic ouvre `BorrowPanel` (`panels.py`), qui reçoit le magasin et le livre
  avant `SidePanel.__init__` car `_build_form` a besoin des utilisateurs ; le menu
  liste `Nom (USRXXX)` dans l'ordre du moteur. `_submit()` appelle
  `LibraryStore.checkout(isbn, user_id)`, puis `save()` ; si `save()` échoue,
  `return_book(isbn)` annule l'emprunt en mémoire, les fichiers restent intacts
  et le panneau affiche l'erreur. Succès : panneau fermé, `_refresh_cards()`,
  `footer.update_stats()` et message du pied de page
  (`« titre » emprunté par Nom (USRXXX).`). `PageFooter.show_message()` est
  public (renommé depuis `_show_message`). Sans utilisateur : menu et bouton
  `Emprunter` désactivés, message « Aucun utilisateur enregistré. ». Aucun
  changement C++ à l'étape 11.
- Retour branché : `BookCard` reçoit aussi `on_return` et l'utilise quand le livre
  est emprunté. `BooksView._return_book()` mémorise `book.borrower_id` et le nom
  de l'emprunteur, appelle `LibraryStore.return_book(isbn)` puis `save()` ; si
  `save()` échoue, `checkout(isbn, borrower_id)` remet l'emprunt en place et les
  fichiers restent intacts. Un `StoreError` (livre déjà disponible, ISBN
  inconnu) rafraîchit la grille et affiche l'erreur. Succès : cartes et
  statistiques rafraîchies, message
  (`« titre » retourné par Nom (USRXXX).`). Aucun panneau : le retour ne demande
  aucun choix, et aucune confirmation n'est demandée (action réversible). Aucun
  changement C++ à l'étape 12.
- Suppression branchée : la corbeille (`TrashIcon`, Canvas avec `cursor="hand2"`)
  lie `<Button-1>` à `on_delete` ; `BooksView._delete_book()` appelle
  `LibraryStore.remove_book(isbn)` **sans confirmation**, puis `save()`. Le C++
  retire l'ISBN des listes d'emprunt. Si `save()` échoue, `store.load()` relit
  l'état exact du disque (livre, ordre, emprunt et listes utilisateurs) au lieu
  de reconstruire ; message d'erreur. Un `StoreError` (livre introuvable)
  rafraîchit la grille. Succès : cartes et statistiques rafraîchies, message
  (`« titre » supprimé.`). Aucun changement C++ à l'étape 13.
- Ajout de livre branché : `Livre +` est exposé en `self.add_book_button` et
  ouvre `AddBookPanel` (`panels.py`), une seule instance à la fois. Le panneau
  propose `Titre`, `Auteur`, `ISBN` et le rappel d'unicité ; `_submit()` appelle
  `LibraryStore.add_book()` puis `save()`. En cas d'`OSError`, `remove_book()`
  annule l'ajout en mémoire et la saisie est conservée ; `StoreError` (champ
  vide, `|`, ISBN déjà présent) est affichée sans vider les champs. Succès :
  champs vidés, message `Livre ajouté : « titre » (ISBN …).`, panneau maintenu
  ouvert, `_refresh_cards()` et `footer.update_stats()`. Aucun changement C++ à
  l'étape 14.
- Toutes les actions de l'écran Livres sont désormais branchées.
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
  est annulé. Après un ajout d'utilisateur réussi, le panneau reste ouvert et le
  champ est vidé ; après un emprunt réussi (`BorrowPanel`), il se ferme et le
  message passe dans le pied de page.

## Conventions
- Code, commentaires, chaînes d'interface et messages de commit en français.
- Préfixes de commit : `[FEAT]`, `[TACHE]`, `[DOCS]`, `[REMISE]`, `[SAUVEGARDE]`.
- Notes de travail : `agent/notes-instructions-projet-llm-agent.md` — avancer une étape
  à la fois (alternance plan/build), exécuter le code avant de commiter.
- Ce fichier est versionné ; ce n'est pas un journal de conversation.
