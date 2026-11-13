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

- `agent/README.md` refers to `agent/data`, but that directory does not exist; fixtures live in `apprentissage/datas/`.
- `CMakeLists.txt` globs `*.cpp`; re-run `cmake ..` after adding or removing source files.
- No tests, linter, or formatter are configured. Verification means compiling (warnings enabled via `-Wall -Wextra -Wpedantic`) and manually exercising the CLI.

## Data and environment gotchas

- `analyse_image/datas/fashion-mnist_{train,test}.csv` are gitignored and not tracked; they must be supplied locally or `classification.ipynb` fails.
- Notebooks use paths relative to their own directory (`datas/...`, `modele/...`). Start Jupyter from `apprentissage/` or `analyse_image/` as appropriate.
- Committed artifacts: `apprentissage/modele/modele_pokemon.mod` (joblib) and `analyse_image/modele/modele.{json,weights.h5}` (Keras). Avoid overwriting unless the task is retraining.
- Python stack: pandas, scikit-learn, matplotlib, seaborn, joblib; plus tensorflow/keras for `analyse_image`. There is no requirements/pyproject/lockfile.
- Root `.venv/` and `.venv312/` are Windows-layout virtualenvs (from another machine) and are gitignored; do not assume they work on Linux.
- Keep user-facing strings, comments, and notebook prose in French to match the repo. Git history uses `[FEAT] ...` / `[REMISE] ...` commit prefixes.

## Partie 3 en cours (agent/)

- Objectif : créer une GUI Python customtkinter qui remplace le CLI de `agent/main.cpp`.
- La logique C++ (Library, Book, User, FileManager) est exposée à Python via pybind11.
- Avancer par petites étapes testables ; tout le travail se fait dans `agent/`.
- Les logs de conversation OpenCode sont rangés dans `agent/chatsLogs/`.
