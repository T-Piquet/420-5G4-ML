# AGENTS.md

## Repository shape
- Three independent ateliers; there is no root build, test, lint, or CI entrypoint.
  - `apprentissage/`: pandas/scikit-learn notebooks (Pokémon win-rate regression).
  - `analyse_image/`: TensorFlow/Keras notebooks (Fashion-MNIST CNN).
  - `agent/`: C++17 CLI `bibliotheque` (CMake), the only compiled project.
- README and UI text are French; keep new user-facing strings and comments French.

## Python notebooks
- Use the local venv: `.venv/bin/python` (Python 3.12; VS Code kernel `.venv (3.12.3)`). It is git-ignored and there is no `requirements.txt`/lockfile.
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

## Verification
- No automated tests, formatter, or linter. Verify C++ with a clean CMake build (warnings are strict: `-Wall -Wextra -Wpedantic`). Verify notebook changes by running the affected notebook from its directory with the venv kernel.
