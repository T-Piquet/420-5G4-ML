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
La sauvegarde se fait au menu 12 et à la sortie (choix 0) ; le menu 13 crée des
copies `.backup` (sans `overwrite_existing`, donc un second passage peut échouer).

## Conventions
- Garder l'UI, les messages et les commentaires en français.
- Code : `main.cpp` (menu CLI) ; `Library` possède des `unique_ptr<Book/User>` ;
  `FileManager` gère la sérialisation ; `Book`/`User` portent le format fichier.
- Devcontainer fourni dans `.devcontainer/` (C++ + CMake + redirection X11).

## Maquette CustomTkinter (plan à implémenter)
Objectif : remplacer le placeholder `gui/app.py` par un prototype desktop
customtkinter reproduisant les actions de `main.cpp`. Aucun changement au C++,
au CMake ni à `data/` ; aucune connexion au backend C++.
Ces fichiers n'existent pas encore.

### Arborescence prévue
```text
agent/gui/
  app.py                    # point d'entrée (remplace le placeholder)
  maquette/
    __init__.py
    theme.py                # palette bleu, typographie, espacements
    models.py               # Book/User/LibraryStore + parsing pipe
    components.py           # sidebar, header, cartes, tableau, modales, toasts
    views.py                # 6 écrans
    window.py               # fenêtre, navigation, état global
```

### Écrans (mapping menu)
- Tableau de bord : cartes statistiques, actions rapides, emprunts en cours.
- Catalogue : recherche titre/auteur (3-4), filtre Tous/Disponibles/Empruntés
  (5-6), ajout (1), suppression avec confirmation (2), emprunt/retour (9-10).
- Utilisateurs : liste avec ID et emprunts, ajout avec ID unique (7-8).
- Emprunts : livres empruntés, retour rapide, état vide.
- Statistiques : total livres, disponibles, empruntés, utilisateurs, taux de
  disponibilité (11).
- Données & sauvegarde : chemins source, boutons Sauvegarder/Créer une
  sauvegarde simulés par toast (12-13).
- Quitter : bouton sidebar avec confirmation (0).

### Données et comportements
- Charger `data/books.txt` et `data/users.txt` en lecture seule via un chemin
  résolu depuis `__file__` ; fallback intégré si absents.
- État en mémoire : ajout/suppression, recherche insensible à la casse, filtres,
  emprunt/retour, statistiques recalculées.
- Validations : ISBN unique, ID utilisateur unique, livre disponible pour
  l'emprunt, livre emprunté pour le retour.
- Suppression d'un livre emprunté : confirmation puis nettoyage de l'emprunt
  côté utilisateur.
- Sauvegarde/backup : toast et « dernière action simulée » ; aucune écriture
  réelle dans `books.txt`, `users.txt` ou `.backup`.
- Modales `CTkToplevel` centrées, fermeture par Échap, validation par Entrée ;
  toasts de succès/erreur et états vides explicites.
- UI et messages en français.

### Style et vérification
- Thème clair bleu bibliothèque : fond `#F5F7FB`, sidebar bleu profond, accent
  `#2563EB`, cartes blanches, badges disponible/emprunté.
- Fenêtre ~1280x800, sidebar ~240 px ; tableaux via `CTkFrame` +
  `CTkScrollableFrame`, sans dépendance type `CTkTable`.
- Lancer depuis `agent/gui` : `./.venv/bin/python app.py` (X11/`DISPLAY` requis).
- Vérifier : `./.venv/bin/python -m py_compile app.py maquette/*.py` puis
  checklist manuelle des actions du menu.

### Hors périmètre
- Persistance réelle, connexion au C++, tests automatisés/CI, packaging.
