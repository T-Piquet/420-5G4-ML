# AGENTS.md

## Layout
- Three independent coursework parts: `apprentissage/` (Pokémon ML), `analyse_image/` (Fashion-MNIST/Keras), and `agent/` (C++17 library core exposed to a CustomTkinter GUI through pybind11). No shared app, package manifest, or root build.
- Notebook prose and user-facing C++/GUI output are French; preserve that convention.

## Verification
- No committed test suite, lint, typecheck, formatter, pre-commit, or CI config exists; don't invent project-wide commands.
- Build the CLI/core with `cmake -S agent -B agent/build && cmake --build agent/build`.
- Build the Python module with `cmake -S agent -B agent/build -DBUILD_PYTHON_BINDINGS=ON -DPython_EXECUTABLE="$PWD/.venv/bin/python" && cmake --build agent/build`. Output: `agent/build/python/bibliotheque_py*.so`.
- `agent/CMakeLists.txt` lists sources explicitly: edit it when adding/removing `.cpp` files. It targets C++17 with `-Wall -Wextra -Wpedantic`; `bibliotheque_core` is PIC so it can feed the shared module.
- `agent/build/` is not committed and is ignored by `agent/.gitignore` (`build/*`).
- VS Code `.vscode/settings.json` hard-codes the CMake source and adds `agent`, `agent/stubs`, `agent/build/python` to Pylance's `extraPaths`. `agent/stubs/bibliotheque_py.pyi` provides typing for the compiled module.
- Run the GUI from the repo root with `PYTHONPATH=agent:agent/build/python .venv/bin/python -m gui.main --data-dir agent/data`. The default data dir is already `agent/data`; relative `--data-dir` values resolve from the current working directory. Use `-m gui.main`, not a direct script run (relative imports).
- GUI needs X11: use `agent/.devcontainer` (it mounts `/tmp/.X11-unix` and passes `DISPLAY`); the root devcontainer does not.

## C++/Python `agent/`
- Core: `book.*`, `user.*`, `library.*`, `filemanager.*`. CLI: `main.cpp`. Bindings: `bindings.cpp` (module name `bibliotheque_py`).
- Python layer: `agent/gui/main.py` (argparse entry point), `agent/gui/app.py` (window, navigation, save-on-close), `agent/gui/service.py` (`LibraryService` wrapper), and `agent/gui/views/` (`dashboard`, `books`, `users`, `borrows`, `stats`, `data`).
- Python deps for the GUI are pinned in `agent/gui/requirements.txt` (`customtkinter`, `pybind11`); `python3-tk` comes from the system/devcontainer.
- `.venv/bin/python` reports Python 3.13.5 and was created from `/usr/bin/python3`, even though `pyvenv.cfg` says 3.12.3.
- `data/books.txt` is `title|author|isbn|1-or-0|borrowerId`; `data/users.txt` is `name|userId|isbn1,isbn2,...`. Preserve these formats.
- CLI: `./agent/build/bibliotheque -d agent/data` (`--data-dir` also works); option `0` auto-saves and exits, option `13` writes `.backup` files. Without `-d`, paths are empty, so nothing loads and saves fail.
- Core behavior: removing a book also removes its ISBN from users' loans; `Library::removeUser` refuses users that still have loans; `createBackup` overwrites existing `.backup` files, returns `bool`, and catches filesystem errors.
- Title/author search in C++ is ASCII-only case-insensitive; accent-insensitive matching is done in Python (`casefold`) in the GUI views.
- GUI loads data at startup; mutations stay in memory, are flagged "modifications non sauvegardées", and are saved on close. The Données page can reload, save, back up, and switch data directories (new `LibraryService` + full view refresh).

## Notebooks
- Notebooks still have no `requirements.txt`/`pyproject.toml`; `.venv/` exists locally with notebook deps plus the GUI deps, and is gitignored. Notebook metadata expects a `.venv` kernel (Python 3.12.3).
- Run notebooks from their own directory: all data/model/image paths are relative (`data/...`, `modele/...`, `images/...`), not repo-root-relative.
- `apprentissage/`: `partie1_2.ipynb` writes tab-separated `data/dataset.csv`; `partie3_entrainement.ipynb` reads it with `delimiter='\t'` and writes `modele/modele_pokemon.mod`; `partie3_predictions.ipynb` loads that committed model. Rerunning the first two overwrites committed artifacts.
- `analyse_image/classification.ipynb` requires `data/analyse_images/fashion-mnist_{train,test}.csv`; they are present locally but gitignored and untracked. It deliberately disables GPU (`tf.config.set_visible_devices([], 'GPU')`) and writes `modele/modele.json` + `modele/modele.weights.h5`.
- `analyse_image/test_model.ipynb` loads those two model files and uses hard-coded `images/image.png`. Its `modele_4_convolutions` option cannot work as shipped: that optional model is trained but never saved.
