# AGENTS.md — Bibliothèque personnelle (TP C++ 420-5G4)

## Projet
Système de gestion de bibliothèque personnelle en C++17.
Version actuelle : application en ligne de commande (menu texte dans `main.cpp`).
Objectif de la Partie 3 : remplacer le menu en ligne de commande par une interface
graphique Python (customTkinter) qui appelle la logique C++ via pybind11.

## Structure
| Fichier | Rôle |
|---|---|
| `book.h/.cpp` | Classe `Book` : titre, auteur, ISBN, disponibilité, ID de l'emprunteur |
| `user.h/.cpp` | Classe `User` : nom, ID, liste des ISBN empruntés |
| `library.h/.cpp` | Classe `Library` : possède les livres et utilisateurs (`vector<unique_ptr<...>>`), recherche, emprunt, retour, statistiques |
| `filemanager.h/.cpp` | Classe `FileManager` : chargement/sauvegarde de `books.txt` et `users.txt`, sauvegarde de secours |
| `activitylogger.h/.cpp` | Classe `ActivityLogger` : écrit les actions dans `journal.log` avec horodatage |
| `main.cpp` | Menu en ligne de commande (14 options) — **à remplacer par la GUI** |
| `data/` | Données de test (`books.txt`, `users.txt`) |
| `CMakeLists.txt` | Compilation de l'exécutable `bibliotheque` |

## Compilation (version ligne de commande)
mkdir build && cd build && cmake .. && make
./bibliotheque -d ../data

## Format des fichiers de données
- `books.txt` : `titre|auteur|isbn|disponible(1/0)|idEmprunteur`
- `users.txt` : une ligne par utilisateur (voir `User::toFileFormat`)

## Menu actuel → écrans prévus de la GUI
| Écran GUI | Options du menu | Méthodes C++ |
|---|---|---|
| Livres (tableau + recherche + tri) | 3, 4, 5, 6, 14 | `getAllBooks`, `getAvailableBooks`, `searchBooksByTitle`, `searchBooksByAuthor` |
| Ajouter / supprimer un livre | 1, 2 | `addBook`, `removeBook`, `findBookByISBN` |
| Utilisateurs | 7, 8 | `getAllUsers`, `addUser`, `generateUserId` |
| Emprunter / retourner | 9, 10 | `checkOutBook`, `returnBook` |
| Statistiques | 11 | `getTotalBooks`, `getAvailableBookCount`, `getCheckedOutBookCount` |
| Fichier (sauvegarder, backup, quitter) | 12, 13, 0 | `FileManager::saveLibraryData`, `loadLibraryData`, `createBackup` |

## Points d'attention (décisions de conception)
1. **Les méthodes `display...()` affichent avec `cout`** : inutilisables dans une GUI.
   La GUI doit utiliser les méthodes qui **retournent** des données (`getAllBooks()`, getters de `Book`/`User`).
   Le tri (option 14) doit retourner une liste triée au lieu de l'afficher.
2. **La journalisation est faite dans `main.cpp`**, pas dans `Library`.
   Si la GUI appelle seulement `Library`, rien ne sera journalisé.
   → Décision à prendre : la GUI appelle `ActivityLogger`, ou on déplace la journalisation dans `Library`.
3. **`Library` possède les objets** (`unique_ptr`) : les méthodes qui retournent `Book*` / `User*`
   doivent être exposées dans pybind11 avec une politique de retour qui **ne détruit pas** les objets
   (`return_value_policy::reference`).
4. Ne pas modifier le comportement de la logique C++ existante sans raison : la GUI s'appuie dessus.

## Méthode de travail
- Planifier avant de coder (mode plan). Le plan détaillé est dans `plan.md`.
- Avancer par **petites étapes testables** : une fonction exposée ou un écran à la fois.
- Après chaque étape : compiler, tester, puis l'humain fait le commit.
- **L'agent ne fait jamais de commit ni de push.**
- En cas d'erreur de compilation, corriger seulement l'erreur signalée.
- Code et commentaires en français.

## État d'avancement
- [x] Logique C++ (TP) terminée
- [x] Environnement : devcontainer, opencode + Ollama, bureau noVNC (port 6080) pour afficher la GUI
- [ ] Phase 1 : plan validé (`plan.md`)
- [ ] Test pybind11 minimal (une fonction)
- [ ] Exposer `Book` et `User`
- [ ] Exposer `Library`, `FileManager`, `ActivityLogger`
- [ ] Écrans de la GUI