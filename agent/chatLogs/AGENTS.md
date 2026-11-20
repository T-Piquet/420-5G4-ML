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
- CMake and g++ are available in the current environment (CMake 3.22.2, g++ 14). The devcontainer under `agent/.devcontainer` also provides them with X11 forwarding. The devcontainer config is under `agent/`, not the repo root.
- Fresh CLI build:
  ```
  cd agent
  rm -rf build && mkdir build && cd build
  cmake .. && make
  ```
- The existing `agent/build/` cache was generated in the devcontainer (`/workspaces/420-5G4-ML/agent`) and may not be reusable elsewhere. Delete it if CMake reports a source-directory mismatch. `build/` and `build-*/` are git-ignored.
- `CMakeLists.txt` uses `file(GLOB *.cpp)` for the CLI: re-run `cmake ..` after adding/removing a source file; `make` alone will not notice it.
- Run from `agent/`: `./build/bibliotheque -d data`. Without `-d`, data file paths are empty and load/save fail.
- Persistence formats: `books.txt` = `title|author|isbn|1|borrowerId`; `users.txt` = `name|userId|isbn1,isbn2`. Writes go through a temporary file then a rename, so an error cannot leave a truncated data file.
- Python bindings: `./bindings/build.sh` builds the `bibliotheque_core` module with the UI venv. It requires pybind11 (installed by `UI/requirements-dev.txt`). In CMake, the module is optional: `-DBUILD_PYTHON_BINDINGS=ON`; it outputs to `agent/UI/app/`.

## Python UI (`agent/UI/`)
- Dedicated venv: `agent/UI/.venv` (git-ignored). Do not reuse the root notebook venv.
- Setup: `cd agent/UI && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`
- Build native module: `cd agent && ./bindings/build.sh`. It uses the UI venv and writes `agent/UI/app/bibliotheque_core*.so` (git-ignored). Re-run it after any C++ change.
- Run: `cd agent/UI && .venv/bin/python main.py`. Requires an X display (`DISPLAY` is forwarded by the devcontainer). Without the native module, the app exits with an explicit build instruction.
- Tests: `cd agent/UI && .venv/bin/python -m pytest -q`. Tests that exercise the native model (library, repository, controller) require the module and skip with an explicit message if it is missing; build it first. GUI smoke tests need a display; use `xvfb-run -a` when `DISPLAY` is unset.
- MVC layout: `app/models/book.py` and `user.py` are dataclasses; `app/models/library.py` is a thin facade over the pybind11 module, which owns the C++ `Book`/`User`/`Library` state. `app/repositories` uses the C++ `FileManager`; `app/views` contains only CTk widgets and receives `BookRow`/`UserRow`; `app/controllers` wires everything; `main.py` is the composition root.
- Bindings source: `agent/bindings/library_bindings.cpp`; CMake target `bibliotheque_core`. Getters return copies to avoid dangling C++ pointers.
- Data: `agent/data/books.txt` (`titre|auteur|isbn|1|` or `0|USRxxx`) and `users.txt` (`nom|id|isbn1,isbn2`). The UI reads at launch and rewrites both files atomically after book add/delete/borrow/return and user add; restore with `git checkout -- agent/data`.
- Screen: sidebar Livres/Utilisateurs/Emprunts/Statistiques (Livres and Utilisateurs are active). Livres has accent-insensitive search by title/author/ISBN, a "Disponibles uniquement" checkbox (combines with search), a book table, and Ajouter / Emprunter↔Retourner / Supprimer. Utilisateurs has accent-insensitive search by name/id, a user table (name, id, borrow count, borrowed titles), and Ajouter.
- UI text and comments are French; identifiers are English.

## Verification
- No formatter or linter. C++ has no automated tests; verify it with a clean CMake build (warnings are strict: `-Wall -Wextra -Wpedantic`). Verify notebook changes by running the affected notebook from its directory with the venv kernel.
- Bindings: `cd agent && ./bindings/build.sh`, then import-check with `cd UI && .venv/bin/python -c "from app import bibliotheque_core; print(bibliotheque_core.__doc__)"`.
- UI: build the native module first, then from `agent/UI`, run `.venv/bin/python -m pytest -q`, then smoke-launch with `timeout 5 .venv/bin/python main.py` (exit code 124 means the window stayed open).
