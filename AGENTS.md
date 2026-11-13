# AGENTS.md

French-language ML workshop with three independent parts. There is no root build/test/lint/CI; each part is run on its own.

## Structure and entrypoints

- `agent/` — C++17 interactive library manager (`bibliotheque`) built with CMake. Entrypoint is `agent/main.cpp`; domain classes are split across `book`, `user`, `library`, and `filemanager`.
- `apprentissage/` — Pokémon analysis/regression. Run notebooks in order: `partie1_2.ipynb` (creates `datas/dataset.csv`) → `partie3_entrainement.ipynb` (creates the model) → `partie3_predictions.ipynb` (loads the model). `main.py` is an older duplicate with broken imports and mixed root-relative paths; treat the notebooks as source of truth.
- `analyse_image/` — Fashion-MNIST CNN. `classification.ipynb` trains and saves the model; `test_model.ipynb` loads it.

## Commands

Build the C++ app from `agent/`:

```sh
mkdir -p build && cd build
cmake ..
make
```

Run it with the real fixtures, from `agent/`:

```sh
./build/bibliotheque -d ../apprentissage/datas
```

- `agent/data/` is the GUI working copy (gitignored), seeded from `apprentissage/datas/` on first launch; fixtures live in `apprentissage/datas/`.
- `CMakeLists.txt` lists sources explicitly; re-run `cmake ..` after adding or removing source files.
- Python service tests: `PYTHONPATH=build python -m unittest discover -s python/tests -v` from `agent/` (headless). No linter or formatter is configured; verification means compiling (warnings enabled via `-Wall -Wextra -Wpedantic`) and running the tests.

## Data and environment gotchas

- `analyse_image/datas/fashion-mnist_{train,test}.csv` are gitignored and not tracked; they must be supplied locally or `classification.ipynb` fails.
- Notebooks use paths relative to their own directory (`datas/...`, `modele/...`). Start Jupyter from `apprentissage/` or `analyse_image/` as appropriate.
- Committed artifacts: `apprentissage/modele/modele_pokemon.mod` (joblib) and `analyse_image/modele/modele.{json,weights.h5}` (Keras). Avoid overwriting unless the task is retraining.
- Python stack: pandas, scikit-learn, matplotlib, seaborn, joblib; plus tensorflow/keras for `analyse_image`. There is no requirements/pyproject/lockfile.
- Root `.venv/` and `.venv312/` are Windows-layout virtualenvs (from another machine) and are gitignored; do not assume they work on Linux.
- Keep user-facing strings, comments, and notebook prose in French to match the repo. Git history uses `[FEAT] ...` / `[REMISE] ...` commit prefixes.

## Partie 3 — GUI Python (agent/)

- GUI customtkinter terminée : onglets Livres, Utilisateurs, Emprunts, Statistiques et barre de statut. Le CLI `main.cpp` reste disponible comme interface historique.
- Le cœur C++ (`Library`, `Book`, `User`, `FileManager`) est exposé à Python via le module `bibliotheque_py` (pybind11, compilé dans `agent/build/`).
- `python/service.py` est l'unique couche d'accès au core pour les vues : conversion des `Book*`/`User*` en dicts Python et API `get_*`, `add_*`, `check_out`, `return_book`, `get_stats`, `save`, `create_backup`.
- `python/app.py` crée la fenêtre, charge `agent/data/` au démarrage et sauvegarde automatiquement à la fermeture (avec message d'erreur si la sauvegarde échoue).
- Vues dans `python/views/` (books, users, loans, stats), tests headless dans `python/tests/test_service.py`.
- Build : depuis `agent/`, `mkdir -p build && cd build && cmake .. && make`.
- GUI : depuis `agent/` avec `.venv` activé, `python python/app.py` (le module compilé est trouvé via `build/`).
- Tests : `PYTHONPATH=build python -m unittest discover -s python/tests -v`.
- CLI : `./build/bibliotheque -d ../apprentissage/datas`.
- `agent/data/` est gitignored et initialisé depuis `apprentissage/datas/` au premier lancement ; ne pas écraser les fixtures suivies.
- `create_backup()` refuse d'écraser un `.backup` existant et lève une `ValueError` affichée dans la barre de statut.
- Les logs de conversation OpenCode sont rangés dans `agent/chatsLogs/`.
