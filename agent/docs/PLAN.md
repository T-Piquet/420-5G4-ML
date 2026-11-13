# Plan — Interface graphique customtkinter + pybind11

Remplacement du menu CLI (`main.cpp`) par une GUI Python qui appelle le core C++ via pybind11.

## Choix retenus

- [x] Données : copie de travail dans `agent/data/`, non suivie par git, initialisée depuis `apprentissage/datas/`.
- [x] La sauvegarde automatique à la fermeture ne doit jamais modifier `apprentissage/datas/` sans avertissement.
- [x] CLI gardé : `main.cpp` et la cible `bibliotheque` restent disponibles jusqu'à validation de la GUI.
- [x] Diagnostic `DISPLAY` avant l'étape GUI (VcXsrv ou WSLg), car le conteneur actuel n'a pas de socket X11.
- [x] Maquettes : 4 onglets en haut (Livres, Utilisateurs, Emprunts, Statistiques) + barre de statut en bas.
- [x] Les méthodes `display*()` qui écrivent sur `cout` ne sont pas utilisées par la GUI.

## Étapes

### Étape 1 — CMake + module pybind11

- [x] Remplacer le `GLOB` des `.cpp` par des cibles explicites.
- [x] Créer `bibliotheque_core` (STATIC) avec `book.cpp`, `user.cpp`, `library.cpp`, `filemanager.cpp`.
- [x] Garder la cible `bibliotheque` (`main.cpp`) liée à `bibliotheque_core`.
- [x] Ajouter `option(BUILD_PYTHON_BINDINGS ... ON)` et `find_package(pybind11 CONFIG REQUIRED)`.
- [x] Créer le module `bibliotheque_py` lié à `bibliotheque_core`.
- [x] Binder `Book`, `User`, `Library`, `FileManager` ; ne pas binder les `display*()`.
- [x] Utiliser `return_value_policy::reference_internal` pour les retours de pointeurs (`findBookByISBN`, `findUserById`, `getAllBooks`, `getAllUsers`, `getAvailableBooks`, `searchBooksBy*`).
- [x] Tester la compilation et l'import du module avec `../apprentissage/datas`.

### Étape 2 — Service Python + tests headless

- [ ] Créer `python/service.py` : encapsuler `Library` + `FileManager`.
- [ ] Convertir immédiatement les `Book*`/`User*` en lignes immuables (`dataclass`/dict) pour éviter les pointeurs C++ persistants côté widgets.
- [ ] Initialiser `agent/data/` depuis les fixtures si le dossier est vide.
- [ ] Créer `python/tests/test_service.py` : chargement, ajout/suppression, emprunt/retour, sauvegarde/rechargement, statistiques, doublons.
- [ ] Tester avec `PYTHONPATH=build python3 -m unittest`, sans fenêtre.

### Étape 3 — Fenêtre customtkinter + onglets

- [ ] Créer un venv `agent/.venv` et `python/requirements.txt` avec `customtkinter`.
- [ ] Diagnostiquer `DISPLAY`, `/tmp/.X11-unix` et un `tkinter.Tk()` minimal.
- [ ] Configurer VcXsrv ou WSLg si nécessaire.
- [ ] Créer `python/app.py` : `CTkTabview` avec Livres, Utilisateurs, Emprunts, Statistiques.
- [ ] Ajouter la barre de statut en bas pour les messages succès/erreur.
- [ ] Ajouter des pages vides et tester l'affichage visuel depuis Windows.

### Étape 4 — Onglet Livres

- [ ] Ajouter le champ de recherche et le choix Titre/Auteur.
- [ ] Ajouter le bouton Rechercher et la case « Disponibles seulement ».
- [ ] Afficher le tableau `ttk.Treeview` : Titre, Auteur, ISBN, Statut.
- [ ] Ajouter le formulaire Titre/Auteur/ISBN et les boutons Ajouter / Supprimer la sélection.
- [ ] Vérifier les doublons d'ISBN et afficher les messages dans la barre de statut.
- [ ] Tester manuellement avec les fixtures.

### Étape 5 — Onglet Utilisateurs

- [ ] Afficher le tableau : Nom, ID, Nb empruntés, ISBNs.
- [ ] Ajouter le formulaire Nom/ID et le bouton Ajouter.
- [ ] Vérifier les doublons d'ID.
- [ ] Tester manuellement.

### Étape 6 — Onglet Emprunts

- [ ] Section Emprunter : liste des livres disponibles + liste des utilisateurs + bouton.
- [ ] Section Retourner : liste des livres empruntés + bouton.
- [ ] Rafraîchir les listes, les tableaux Livres/Utilisateurs et les statistiques après chaque opération.
- [ ] Tester le scénario complet emprunt → retour.

### Étape 7 — Onglet Statistiques

- [ ] Afficher les 4 cartes : Livres, Disponibles, Empruntés, Utilisateurs.
- [ ] Ajouter les boutons Sauvegarder et Créer une sauvegarde.
- [ ] Rafraîchir les cartes après chaque action.
- [ ] Tester manuellement.

### Étape 8 — Persistance et finition

- [ ] Charger les données au démarrage depuis `agent/data/`.
- [ ] Implémenter la sauvegarde explicite et la sauvegarde automatique à la fermeture.
- [ ] Gérer les erreurs C++/fichiers dans la barre de statut, notamment si un `.backup` existe déjà.
- [ ] Mettre à jour le README et `AGENTS.md`.
- [ ] Décider du sort final de `main.cpp`.
- [ ] Tester fermeture/réouverture et vérifier les fichiers écrits.

## Fichiers prévus

```text
agent/
  CMakeLists.txt
  .gitignore                 # + .venv/ et data/
  data/                      # copie de travail non suivie
  python/
    bindings.cpp
    app.py
    service.py
    views/{books,users,loans,stats}.py
    tests/test_service.py
    requirements.txt
```

## Contenu des onglets

- [ ] Livres : recherche (Titre/Auteur), « Disponibles seulement », tableau (Titre, Auteur, ISBN, Statut), formulaire d'ajout et suppression de la sélection.
- [ ] Utilisateurs : tableau (Nom, ID, Nb empruntés, ISBNs), formulaire d'ajout.
- [ ] Emprunts : liste déroulante des livres disponibles + utilisateurs, et liste déroulante des livres empruntés pour le retour.
- [ ] Statistiques : 4 cartes + boutons Sauvegarder et Créer une sauvegarde.
- [ ] Fermeture de la fenêtre : sauvegarde automatique.

## Points d'attention

- [ ] Le module Python doit être compilé dans le même conteneur Linux que le Python qui l'importe.
- [ ] Les fichiers `apprentissage/datas/{books,users}.txt` sont suivis par git : ne pas les écraser.
- [ ] `FileManager::createBackup()` peut échouer si le `.backup` existe déjà ; intercepter l'erreur côté Python.
