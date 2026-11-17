# Partie 4 — Journal d'implémentation

- **Date** : 2026-11-17
- **Outil** : OpenCode
- **Agent / modèle** : Big Pickle
- **Environnement** : WSL2, Python 3.13.5, CMake 3.22.2, g++ 14.2.0,
  pybind11 2.13.6, customtkinter 6.0.0, pytest 9.2.0.

## Demande de l'utilisateur

> Le plan est validé. Passe maintenant à son implémentation complète.
>
> Respecte les contraintes du plan :
> - Réutilise les classes C++ existantes et conserve le programme console
>   fonctionnel.
> - Crée les bindings pybind11 et l'interface graphique customTkinter.
> - Implémente les fonctionnalités existantes de la bibliothèque sans ajouter
>   de fonctionnalités inutiles.
> - Modifie le moins possible le code C++ existant.
> - Ne travaille jamais directement sur les vrais fichiers de données pendant
>   les tests. Utilise des copies temporaires.
> - Compile le projet et exécute les tests possibles. Signale clairement les
>   tests graphiques nécessitant une vérification manuelle.
> - Documente les étapes, les décisions et les tests dans chatsLogs/
>   conformément au TP, sans inventer d'échanges ni de résultats.
> - Fais des commits Git réguliers aux étapes importantes, sans faire de push
>   ni créer de Pull Request pour l'instant.
>
> Commence l'implémentation et poursuis jusqu'à obtenir une application
> fonctionnelle. Si une erreur survient, tente de la corriger et vérifie à
> nouveau.

## Étapes réalisées

1. **Environnement Python**
   - Création de `agent/.venv`.
   - Installation de `customtkinter` (6.0.0) et `pytest` (9.2.0).
   - Vérification de Tk : `DISPLAY=:0`, socket `/tmp/.X11-unix/X0` présent,
     fenêtre Tk créée puis détruite avec succès (1920 × 1080).

2. **Bindings pybind11**
   - Création de `agent/bindings/bindings.cpp`.
   - Exposition de `Book`, `User`, `Library` et `FileManager`.
   - Les méthodes de recherche et de listage renvoient des copies de `Book` /
     `User` pour éviter de transférer la propriété des `unique_ptr`.
   - Ajout de `book_exists` et `user_exists` pour les contrôles de doublons.

3. **CMake**
   - Ajout de l'option `BUILD_PYTHON_BINDINGS` (activée par défaut).
   - Ajout de `find_package(pybind11 CONFIG REQUIRED)` et de
     `add_subdirectory(bindings)`.
   - Création de `agent/bindings/CMakeLists.txt`, avec sortie du module dans
     `agent/build/python/`.
   - La cible console `bibliotheque` reste inchangée.

4. **Interface graphique**
   - Création de `agent/gui/app.py`.
   - Onglets Livres, Utilisateurs, Emprunts et Données.
   - Recherche par titre/auteur, affichage de tous les livres ou des livres
     disponibles, ajout/suppression de livres, ajout d'utilisateurs,
     emprunt/retour, statistiques, sauvegarde et création de `.backup`.
   - Ajout de l'option `--data-dir` (par défaut `agent/data`).
   - Sauvegarde uniquement sur action explicite ou confirmation à la fermeture.

5. **Tests**
   - Création de `agent/tests/conftest.py`, `test_bindings.py`,
     `test_cli.py` et `test_gui_smoke.py`.
   - Toutes les opérations de test utilisent une copie temporaire de
     `agent/data`.
   - Une garde de session compare les empreintes SHA-256 des vrais fichiers
     `books.txt` et `users.txt` avant/après les tests.

6. **Documentation et Dev Container**
   - Mise à jour de `README.md` et `agent/README.md`.
   - Mise à jour de `AGENTS.md`.
   - Ajout d'un `postCreateCommand` dans le devcontainer pour créer
     `agent/.venv` et installer `agent/requirements.txt`.
   - Ajout des règles `.gitignore` pour le venv, les caches et les `.backup`.

## Fichiers créés

- `agent/bindings/bindings.cpp`
- `agent/bindings/CMakeLists.txt`
- `agent/gui/app.py`
- `agent/requirements.txt`
- `agent/tests/conftest.py`
- `agent/tests/test_bindings.py`
- `agent/tests/test_cli.py`
- `agent/tests/test_gui_smoke.py`
- `chatsLogs/partie4_planification.md`
- `chatsLogs/partie4_implementation.md`
- `chatsLogs/partie4_tests.md`

## Fichiers modifiés

- `agent/CMakeLists.txt`
- `agent/.gitignore`
- `agent/.devcontainer/devcontainer.json`
- `agent/README.md`
- `README.md`
- `AGENTS.md`

## Fichiers métier C++ non modifiés

- `agent/book.h`, `agent/book.cpp`
- `agent/library.h`, `agent/library.cpp`
- `agent/user.h`, `agent/user.cpp`
- `agent/filemanager.h`, `agent/filemanager.cpp`
- `agent/main.cpp`

## Commandes principales exécutées

```bash
python3 -m venv agent/.venv
source agent/.venv/bin/activate
pip install customtkinter pytest

cmake -S agent -B agent/build
cmake --build agent/build -j

PYTHONPATH=agent/build/python pytest -q agent/tests
```

Résultat obtenu : **9 tests réussis**.

## Limite restante

Le test GUI automatique crée la fenêtre, vérifie les tableaux et exécute les
actions principales, mais il ne juge pas l'apparence visuelle. Une vérification
manuelle de la mise en page et de l'affichage WSL reste nécessaire.
