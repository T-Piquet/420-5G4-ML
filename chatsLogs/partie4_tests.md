# Partie 4 — Journal des tests

- **Date** : 2026-11-17
- **Environnement** : WSL2, Python 3.13.5, pybind11 2.13.6,
  customtkinter 6.0.0, pytest 9.2.0, CMake 3.22.2.
- **Affichage** : `DISPLAY=:0`, serveur X11 disponible.

## 1. Compilation complète

Commande :

```bash
source agent/.venv/bin/activate
cmake -S agent -B agent/build
cmake --build agent/build -j
```

Résultat :

```text
[ 91%] Built target bibliotheque
[100%] Built target bibliotheque_py
```

Le module produit est :

```text
agent/build/python/bibliotheque_py.cpython-313-x86_64-linux-gnu.so
```

Un build propre dans un répertoire séparé a également été testé :

```bash
rm -rf /tmp/biblio-build
cmake -S agent -B /tmp/biblio-build
cmake --build /tmp/biblio-build -j
PYTHONPATH=/tmp/biblio-build/python python -c "import bibliotheque_py"
```

Résultat : import du module réussi.

## 2. Compilation du programme console seul

```bash
cmake -S agent -B /tmp/biblio-build-cli -DBUILD_PYTHON_BINDINGS=OFF
cmake --build /tmp/biblio-build-cli -j
```

Résultat : binaire `bibliotheque` produit, option Python désactivée.

## 3. Tests automatisés

Commande :

```bash
cd /workspaces/420-5G4-ML
source agent/.venv/bin/activate
PYTHONPATH=agent/build/python pytest -q agent/tests
```

Résultat exact obtenu :

```text
.........                                                                [100%]
9 passed in 2.11s
```

### Tests des bindings (`agent/tests/test_bindings.py`)

- `test_load_existing_data` : chargement de 41 livres et 25 utilisateurs
  depuis une copie temporaire.
- `test_add_search_and_remove_book` : ajout, recherche par titre et auteur,
  suppression, contrôle d'existence.
- `test_add_user_and_duplicate_check` : ajout d'un utilisateur et contrôle
  d'existence.
- `test_borrow_and_return_book` : emprunt, refus d'un second emprunt, retour,
  mise à jour du livre et de l'utilisateur.
- `test_borrow_refused_for_unknown_user` : refus d'un emprunt avec un
  utilisateur inconnu.
- `test_save_and_reload_roundtrip` : sauvegarde puis rechargement dans une
  nouvelle instance.
- `test_create_backup_and_existing_backup_error` : création des fichiers
  `.backup`, puis vérification de l'exception existante lors d'une deuxième
  sauvegarde.

### Test du programme console (`agent/tests/test_cli.py`)

- `test_console_still_works_without_touching_tracked_data` : lancement du
  binaire avec l'option `0`, sur une copie temporaire. Le code de sortie est
  0 et les empreintes des fichiers de la copie sont inchangées.

### Test graphique (`agent/tests/test_gui_smoke.py`)

- `test_gui_workflow` : création de la fenêtre, vérification des tableaux et
  des statistiques, ajout/suppression de livre, ajout d'utilisateur,
  emprunt/retour, sauvegarde, rechargement et création des `.backup`.
- Le test est ignoré automatiquement si `DISPLAY` n'est pas défini.
- Ce test ne remplace pas une vérification visuelle : la taille, la lisibilité,
  les couleurs et le rendu des onglets doivent être contrôlés manuellement.

## 4. Protection des données suivies par Git

`agent/tests/conftest.py` contient une garde de session :

- calcul des SHA-256 de `agent/data/books.txt` et `agent/data/users.txt` avant
  les tests ;
- nouvelle vérification après la suite ;
- échec explicite si l'un des deux fichiers a changé.

La suite `9 passed` confirme que la garde n'a détecté aucune modification.

## 5. Vérifications manuelles restant à faire

1. Lancer l'application sur une copie temporaire :

   ```bash
   rm -rf /tmp/biblio-data
   cp -r agent/data /tmp/biblio-data
   source agent/.venv/bin/activate
   PYTHONPATH=agent/build/python python agent/gui/app.py --data-dir /tmp/biblio-data
   ```

2. Vérifier visuellement :
   - affichage des quatre onglets ;
   - lisibilité des tableaux et des statistiques ;
   - redimensionnement de la fenêtre ;
   - apparence sous WSL / serveur X11.

3. Tester la fermeture avec « Oui », « Non » et « Annuler » et vérifier que
   les fichiers de `/tmp/biblio-data` sont écrits uniquement lorsque demandé.

4. Vérifier qu'après ces essais, `git status --short agent/data` reste vide.
