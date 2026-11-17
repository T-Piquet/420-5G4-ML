# Partie 4 — Journal de planification

- **Date** : 2026-11-17
- **Outil** : OpenCode
- **Agent / modèle** : Big Pickle
- **Mode** : Plan (aucun fichier modifié)

## Demande de l'utilisateur

> Analyse le projet C++ existant dans le dossier agent et prépare un plan
> d'implémentation pour la dernière partie de mon TP : remplacer l'interface
> console de la bibliothèque personnelle par une interface graphique Python
> utilisant customTkinter et une intégration avec C++ via pybind11.
>
> Contraintes importantes :
> - Réutiliser les classes C++ existantes (Book, Library, User, FileManager).
> - Conserver les fonctionnalités du programme actuel.
> - Modifier le moins possible le code C++ existant.
> - Ne pas réécrire la logique métier en Python.
> - Préserver les fichiers de données existants et éviter de les écraser
>   pendant les tests.
> - Garder une solution simple, fonctionnelle et adaptée à un TP étudiant.
> - Vérifier les fichiers CMake et la configuration du Dev Container.
> - Prévoir comment afficher l'interface graphique depuis notre environnement
>   Linux/WSL.
> - Prévoir les tests, les commits Git et l'exportation des échanges IA dans
>   chatsLogs/.
>
> Présente un plan clair avec les fichiers à créer ou modifier, les étapes dans
> le bon ordre et les commandes nécessaires.
>
> Pour l'instant, ne modifie aucun fichier et ne génère aucun code. Je veux
> seulement le plan.

## Synthèse du plan proposé

- Conserver le binaire console `bibliotheque` et ajouter une nouvelle entrée
  Python, sans modifier les fichiers métier C++.
- Créer un module `bibliotheque_py` avec pybind11 dans `agent/bindings/`, en
  dehors du `GLOB` CMake de l'exécutable.
- Renvoyer des copies de `Book` / `User` vers Python pour éviter les problèmes
  de possession mémoire des `unique_ptr` de `Library`.
- Créer une interface customtkinter dans `agent/gui/app.py` avec les onglets
  Livres, Utilisateurs, Emprunts et Données.
- Garder les données C++ comme source de vérité : l'interface ne fait que
  collecter les saisies, appeler les méthodes C++ et afficher les résultats.
- Utiliser un répertoire de données configurable (`--data-dir`) et des copies
  temporaires pour tous les tests.
- Créer `agent/tests/` avec une garde qui vérifie que `agent/data/books.txt` et
  `agent/data/users.txt` ne sont jamais modifiés pendant la suite de tests.
- Mettre à jour le Dev Container pour créer un venv Python et installer
  customtkinter, en conservant le montage X11 et `--net=host`.
- Prévoir trois commits Git distincts et les journaux dans `chatsLogs/`.

## Décisions validées

- Le programme console reste fonctionnel.
- Aucun changement dans `book.*`, `library.*`, `user.*`, `filemanager.*` ou
  `main.cpp`.
- Les bindings exposent des copies pour les listes et des booléens pour les
  vérifications d'existence.
- La GUI ne sauvegarde que sur action explicite ou confirmation à la fermeture.
- Les tests et essais manuels utilisent une copie de `agent/data` dans `/tmp`.

## Statut

Plan validé par l'utilisateur, puis passage en mode implémentation.
