# AGENTS.md

School lab with 3 parts plus a standalone `agent/gui/` test app. No CI, tests, linter, or root build/package manifest; verification is manual.

## Layout
- `apprentissage/` — Jupyter notebooks: Pokémon data prep + scikit-learn training/prediction.
- `analyse_image/` — Jupyter notebooks: Fashion-MNIST CNN (Keras/TensorFlow).
- `agent/` — C++17 CLI "bibliotheque" app, CMake, X11 devcontainer.
- `agent/gui/` — Standalone Python `customtkinter` window with a C++ `pybind11` extension; local venv in `agent/gui/.venv`.

## C++ (`agent/`)
- Build: `cmake -S agent -B agent/build && cmake --build agent/build -j`
- Binary: `agent/build/bibliotheque`
- Always pass a data dir when running from the repo root: `agent/build/bibliotheque -d agent/data`. Without `-d`, `FileManager` receives empty filenames and load/save fail.
- Saving in the app overwrites `agent/data/books.txt` and `users.txt` (tracked fixtures); copy them when experimenting.
- CMake globs `agent/*.cpp`; re-run CMake after adding/removing source files. C++17 with `-Wall -Wextra -Wpedantic`.
- `agent/build/` contents are gitignored; never commit build artifacts.
- Devcontainer config exists only in `agent/.devcontainer`; open `agent/` in VS Code to use it.

## GUI test app (`agent/gui/`)
- UI is Python-only (`customtkinter`); C++ exposes `_cpp_backend` via `pybind11` and is imported by `agent/gui/main.py`.
- Venv is local at `agent/gui/.venv` (gitignored). Recreate it with:
  `python3 -m venv agent/gui/.venv && agent/gui/.venv/bin/python -m pip install customtkinter`
- Build the C++ extension:
  `cmake -S agent/gui -B agent/gui/build -DPython_EXECUTABLE="$PWD/agent/gui/.venv/bin/python" -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)" && cmake --build agent/gui/build -j`
- `pybind11_DIR` is required because its CMake config is in a nonstandard system path. Build with the venv interpreter so the extension ABI matches.
- Smoke test without opening a window:
  `agent/gui/.venv/bin/python -c "import sys; sys.path.insert(0, 'agent/gui/build'); import _cpp_backend; print(_cpp_backend.message())"`
- Run: `agent/gui/.venv/bin/python agent/gui/main.py`. Requires a live X server (`DISPLAY` + `/tmp/.X11-unix`); otherwise only the smoke test is possible. The `agent/.devcontainer` X11 setup covers this app.
- `agent/gui/build/` and `agent/gui/.venv/` are gitignored; never commit them.

## Notebooks
- Notebooks use relative paths (`datas/`, `modele/`). Run Jupyter with the notebook's directory as CWD (e.g. `jupyter lab --notebook-dir apprentissage` and execute there). Running from the repo root breaks file access.
- Local `.venv` dirs are gitignored and currently broken: created for Python 3.12 but only Python 3.13 is installed, so `import sklearn` / `import tensorflow` fails. Recreate them before use:
  - `python3 -m venv apprentissage/.venv && apprentissage/.venv/bin/pip install pandas numpy matplotlib seaborn scikit-learn joblib`
  - `python3 -m venv analyse_image/.venv && analyse_image/.venv/bin/pip install tensorflow keras pillow pandas numpy matplotlib scikit-learn`
- No `requirements.txt` or `pyproject.toml` exists; dependencies above are inferred from notebook imports, not pinned.
- `analyse_image/datas/` is gitignored, so the Fashion-MNIST CSVs are absent on a fresh clone but required by `classification.ipynb`.
- Notebooks overwrite tracked artifacts: `apprentissage/datas/dataset.csv`, `apprentissage/modele/modele_pokemon.mod`, `analyse_image/modele/modele.json` and `.weights.h5`. Commit only intentional changes.
- Training is expensive (up to 50 epochs); TensorFlow is forced CPU-only in `classification.ipynb`.

## Conventions
- User-facing strings, notebook prose, and comments are French; keep that for UI/docs.
- Commit messages in history use bracket prefixes: `[FEATURE]`, `[CREATION]`, `[REMISE]`, `[REFRACTOR]`, `[test]`. Follow that style if asked to commit.
