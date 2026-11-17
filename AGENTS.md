# AGENTS.md

Atelier ML (school lab). The three analysis parts live under `agent/`; the
root `README.md` previously pointed at the wrong directories. Part 4 adds a
Python GUI around the existing C++ library app.

## C++ CLI (`agent/`)

Build from the repo root (CMake ≥ 3.21, C++17, pybind11 needed by default):
```bash
cmake -S agent -B agent/build
cmake --build agent/build -j
```
Use `-DBUILD_PYTHON_BINDINGS=OFF` for a CLI-only build.

Run from `agent/build`, pointing at a data dir:
```bash
./bibliotheque -d ../data       # also --data-dir
```

- `CMakeLists.txt` globs `agent/*.cpp` into one `bibliotheque` executable. Do not add a second `main()`; after adding/removing a `.cpp`, re-run CMake because the glob is only evaluated at configure time. Keep new C++ (e.g. `bindings/`) in subdirectories.
- Python binding sources are `agent/bindings/bindings.cpp`; the module `bibliotheque_py` is built to `agent/build/python/`. It exposes copies of `Book`/`User` lists because `Library` owns them via `unique_ptr`; do not return those internal pointers directly.
- No C++ unit tests or CI. Compilation uses `-Wall -Wextra -Wpedantic`; new code should be warning-free. Python tests exist for Part 4.
- Data files are pipe-separated: `books.txt` = `title|author|isbn|available(1/0)|borrowerId`, `users.txt` = `name|userId|isbn,isbn`.
- Without `-d`, file names are empty and nothing loads/saves. With `-d`, the CLI **rewrites the tracked fixtures on exit**; test against a temp copy of `agent/data`.
- UI text and docs are French; C++ comments are English.
- `.devcontainer/` (inside `agent/`) mounts the X11 socket with `--net=host`, forwards `DISPLAY`, and runs a `postCreateCommand` creating `agent/.venv`. `.vscode/settings.json` hardcodes a Windows CMake source path; ignore or repoint it to `agent`.

## Part 4 GUI (`agent/gui/`)

```bash
python3 -m venv agent/.venv
source agent/.venv/bin/activate
pip install -r agent/requirements.txt
cmake -S agent -B agent/build && cmake --build agent/build -j

PYTHONPATH=agent/build/python python agent/gui/app.py --data-dir /tmp/biblio-data
```
`--data-dir` defaults to `agent/data`; use a temp copy for manual tests. The GUI only writes on explicit Save or on close confirmation.

Tests:
```bash
source agent/.venv/bin/activate
PYTHONPATH=agent/build/python pytest -q agent/tests
```
`agent/tests/conftest.py` copies `agent/data` into `tmp_path` and has a session guard asserting the tracked `books.txt`/`users.txt` hashes never change. The GUI smoke test requires `DISPLAY` and is skipped otherwise; visual layout still needs manual review. `FileManager::create_backup()` throws if a `.backup` already exists; the GUI catches it.

## Notebooks

Always start Jupyter in the notebook's own directory; all paths are relative to it.

- `agent/apprentissage/`: reads `../data/pokedex.csv` / `../data/combats.csv`, writes `modele/` artifacts.
- `agent/analyse_image/`: reads `datas/…` and `modele/…`.

Required order for the learning part: `partie1_2.ipynb` builds `agent/data/dataset.csv` (tab-separated) → `partie3_entrainement.ipynb` trains and overwrites `agent/apprentissage/modele/modele_pokemon.mod` → `partie3_predictions.ipynb` loads that model.

- `agent/data/dataset.csv` and both model artifacts are tracked, but generated. Retraining silently rewrites committed files, including a multi-MB `.mod` and `.weights.h5`.
- `agent/analyse_image/datas/` is gitignored (~200 MB of Fashion-MNIST CSVs/IDX files); a fresh clone lacks them, so `classification.ipynb` cannot run until the data is supplied.
- `classification.ipynb` forces CPU via `tf.config.set_visible_devices([], 'GPU')`.
- Python is 3.13. The ML dependencies (pandas, numpy, matplotlib, seaborn, scikit-learn, joblib, tensorflow/keras, pillow) have no lockfile; Part 4 only needs `agent/requirements.txt`.
