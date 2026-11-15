# AGENTS.md

French-language course project with three independent areas. No CI, test suite, or linter configured; verify changes by compiling/running the affected area.

## Layout
Paths below are relative to the repository root (the parent of `agent/`).

- `agent/` — C++17 CMake console app `bibliotheque` (personal library manager). Sources are `agent/*.{h,cpp}`; sample data in `agent/data/`.
- `agent/gui/` — Python CustomTkinter GUI for the library. Sources are in `agent/gui/.venv/`; dependencies are isolated in `agent/gui/env/` (gitignored). It reuses `agent/data/`.
- `apprentissage/` — Pokemon ML notebooks (pandas/scikit-learn regression), Parts 1–3.
- `analyse_image/` — Fashion-MNIST Keras CNN notebooks; model committed in `analyse_image/modele/`.
- `datas/` — Pokemon CSVs; `modele/modele_pokemon.mod` is the joblib model. Both committed.
- Top-level `README.md` is sparse; trust config/files over it.

## C++ agent
Build from the repository root (parent of `agent/`):
```
cmake -S agent -B agent/build
cmake --build agent/build
```
Or from `agent/build`: `cmake .. && make`. `agent/build/` is gitignored; never edit generated files there.

- Binary: `agent/build/bibliotheque`. Run with sample data from `agent/build`: `./bibliotheque -d ../data`.
- Only `-d <dir>` / `--data-dir <dir>` is accepted; there is no `--help`.
- `CMakeLists.txt` uses `file(GLOB *.cpp)`: after adding/removing a `.cpp`, re-run `cmake ..` or the new file is silently omitted.
- Keep the build clean: `-Wall -Wextra -Wpedantic` are enabled.
- Data is newline-delimited and pipe-separated:
  - `books.txt`: `title|author|isbn|1-or-0|borrowerId`
  - `users.txt`: `name|userId|isbn1,isbn2,...`
- No test framework; exercise behavior through the menu or piped stdin. 

## Python GUI
- Source lives literally in `agent/gui/.venv/` (it is not a virtualenv); the actual venv is `agent/gui/env/` (gitignored). Do not rename either path.
- Set up from the repository root: `python3 -m venv agent/gui/env` then `agent/gui/env/bin/python -m pip install -r agent/gui/.venv/requirements.txt`.
- Run with X11: `DISPLAY=:0 agent/gui/env/bin/python agent/gui/.venv/app.py --data-dir agent/data`.
- The GUI reuses `agent/data/books.txt` and `agent/data/users.txt`; without `--data-dir`, it searches upward for a `data/` directory containing both files.
- `customtkinter==6.0.0` is pinned in `agent/gui/.venv/requirements.txt`.
- Theme colors in `agent/gui/.venv/theme.py` are `(light, dark)` tuples; use `theme.*` for widget colors so `ctk.set_appearance_mode()` can recolor the running UI. The selected mode is persisted in `~/.config/bibliotheque/settings.json`.

## Python / notebooks
- Use the root `.venv` (Python 3.13, gitignored): `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- Notebook paths are relative to each notebook's directory. Launch Jupyter with cwd = `apprentissage/` or `analyse_image/`; paths like `../datas/` and `datas/` break otherwise.
- Notebook order matters: `apprentissage/partie1_2.ipynb` writes `../datas/dataset.csv` (tab-separated), which `partie3_entrainement.ipynb` reads; `partie3_predictions.ipynb` then loads `../modele/modele_pokemon.mod`.
- `modele/modele_pokemon.mod` is a committed joblib artifact; loading needs the pinned scikit-learn (1.9.1). Retraining overwrites it.
- `analyse_image/datas/` is gitignored, so a fresh clone lacks the Fashion-MNIST CSVs. Only the model/images are committed.
- `classification.ipynb` disables GPU (`tf.config.set_visible_devices([], 'GPU')`); the 50-epoch augmented training run is slow.
- The Keras model is loaded via `model_from_json` + `load_weights` from `analyse_image/modele/`, not `load_model`.

## Conventions
- User-facing text, comments, and commits are French. Existing commit prefixes: `[REMISE]`, `[FEAT]`, `[TACHE]`.
- Never commit `agent/build/`, `.venv/`, `agent/gui/env/`, or `analyse_image/datas/` (all gitignored).
- `agent/.devcontainer/` is the intended C++ environment (CMake 3.22.2, X11). `.vscode/settings.json` has a stale absolute `cmake.sourceDirectory`; use `agent/` instead.
