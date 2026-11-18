# AGENTS.md

## Repository shape
- Three independent ateliers; there is no root build, test, lint, or CI entrypoint.
  - `apprentissage/`: pandas/scikit-learn notebooks (Pokémon win-rate regression).
  - `analyse_image/`: TensorFlow/Keras notebooks (Fashion-MNIST CNN).
  - `agent/`: C++17 CLI `bibliotheque` (CMake), the only compiled project; it
    also contains the Python/customtkinter UI under `agent/UI/`.
- README and UI text are French; keep new user-facing strings and comments French.

## Python notebooks
- Use the local venv: `.venv/bin/python` (currently Python 3.13.5; check with `.venv/bin/python --version`). It is git-ignored and there is no `requirements.txt`/lockfile.
- The venv has `ipykernel` but no JupyterLab/Notebook server; use VS Code's notebook UI.
- Notebooks use relative `datas/` and `modele/` paths. Run them with the notebook's own directory as cwd; running from the repo root breaks every path.
- `analyse_image`: run `classification.ipynb` before `test_model.ipynb`; the former writes `modele/modele.json` and `modele/modele.weights.h5`.
- `apprentissage`: `partie1_2.ipynb` writes `datas/dataset.csv` (tab-separated); `partie3_entrainement.ipynb` reads it and writes `modele/modele_pokemon.mod`; `partie3_predictions.ipynb` loads that model.
- `analyse_image/datas/.gitignore` ignores `*`: Fashion-MNIST CSVs/IDX files exist only locally. `apprentissage/datas/*` is tracked.

## C++ (`agent/`)
- CMake is not installed on the host; `g++`/`make` are. Build inside `agent/.devcontainer` (CMake 3.22.2, X11 forwarding). The devcontainer config is under `agent/`, not the repo root.
- Fresh build:
  ```
  cd agent
  rm -rf build && mkdir build && cd build
  cmake .. && make
  ```
- The existing `agent/build/` cache was generated in the devcontainer (`/workspaces/420-5G4-ML/agent`) and is not reusable on the host. Delete it if CMake reports a source-directory mismatch. `build/` is git-ignored.
- `CMakeLists.txt` uses `file(GLOB *.cpp)`: re-run `cmake ..` after adding/removing a source file; `make` alone will not notice it.
- Run from `agent/`: `./build/bibliotheque -d data`. Without `-d`, data file paths are empty and load/save fail.
- Persistence formats: `books.txt` = `title|author|isbn|1|borrowerId`; `users.txt` = `name|userId|isbn1,isbn2`.

## Python UI (`agent/UI/`)
- Dedicated venv: `agent/UI/.venv` (git-ignored). Do not reuse the root notebook venv.
- Setup: `cd agent/UI && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`
- Run: `cd agent/UI && .venv/bin/python main.py`. Requires an X display (`DISPLAY` is forwarded by the devcontainer).
- Tests: `cd agent/UI && .venv/bin/python -m pytest -q`. GUI smoke tests need a display; use `xvfb-run -a` when `DISPLAY` is unset.
- MVC layout: `app/models` holds pure state/logic with no Tk imports; `app/views` holds CTk widgets only; `app/controllers` wires the two without creating widgets; `main.py` is the composition root.
- UI text and comments are French; identifiers are English.
- The initial window shows a label and a counter to exercise view → controller → model → view.

## Verification
- No formatter or linter. C++ has no automated tests; verify it with a clean CMake build (warnings are strict: `-Wall -Wextra -Wpedantic`). Verify notebook changes by running the affected notebook from its directory with the venv kernel.
- UI: from `agent/UI`, run `.venv/bin/python -m pytest -q`, then smoke-launch with `timeout 5 .venv/bin/python main.py` (exit code 124 means the window stayed open).
