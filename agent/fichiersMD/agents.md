# Repository notes

- Three independent parts (root README only maps them): `apprentissage/` (Pokémon notebooks), `analyse_image/` (Fashion-MNIST CNN notebooks), `agent/` (C++17 CMake CLI + pybind11 module + Tkinter UI). There is no root build/test/lint command.
- No CI, test targets, pre-commit, lockfile, or lint/typecheck config. Verification is: build `agent/`, run a Python smoke test on a copy of `agent/data/`, instantiate the UI, and execute only the affected notebook(s).

## C++ `agent/`

- Build: `cmake -S agent -B agent/build && cmake --build agent/build` builds the CLI. Add `-Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)"` to also build `bibliotheque_py`; without pybind11 the module is skipped with a STATUS message and the CLI still builds. Outputs in `agent/build/` (ignored/generated): `bibliotheque` and `bibliotheque_py*.so`.
- CMake requires >=3.21, C++17, explicit source lists (no `file(GLOB)` anymore): `bibliotheque_core` static lib (`book.cpp`, `user.cpp`, `library.cpp`, `filemanager.cpp`, `session.cpp`), `bibliotheque` CLI (`main.cpp`), `bibliotheque_py` (`bindings.cpp`). Warnings are `-Wall -Wextra -Wpedantic`; the core is compiled PIC so it can be linked into the Python module.
- Run: `./agent/build/bibliotheque -d agent/data` (also `--data-dir`). Paths are relative to the process cwd; without `-d` the app starts with empty filenames and saves fail.
- The CLI reads `data/books.txt` and `data/users.txt` at startup and overwrites both on menu "12" or quit "0"; use a copy of `agent/data/` when testing destructive flows.
- It is a terminal/menu app (French prompts). X11 forwarding in `agent/.devcontainer/` is now only needed to display the Tkinter window through VS Code.

## Python bindings `agent/`

- `session.h` / `session.cpp`: `LibrarySession(data_dir)` owns a fresh `Library` and a `FileManager` and loads data at construction. Facade API: `reload`, add/remove/search books, add/list users, `check_out_book`, `return_book`, `stats`, `save`, `backup`. Duplicate ISBN/ID are rejected; `reload()` resets the `Library` because `loadLibraryData()` appends; `remove_book()` returns the loan first; `backup()` catches filesystem errors; `messages` exposes the `FileManager` status messages.
- `bindings.cpp`: `Book` (`title`, `author`, `isbn`, `available`, `borrower_id`) and `User` (`name`, `user_id`, `borrowed_books`) are read-only copies; `LibrarySession` exposes the snake_case API above. Low-level mutations and `toString`/`toFileFormat` are not bound.
- `FileManager` messages go through an optional reporter callback: the default writes to `cout` (CLI output unchanged), while `LibrarySession` collects them instead.
- Import check: `PYTHONPATH=agent/build python3 -c "import bibliotheque_py as bp; print(bp.LibrarySession('agent/data').stats())"`. Use a copy of `agent/data/` for add/save/backup/reload tests.

## Interface Tkinter `agent/interface_tk.py`

- Mockup: `agent/maquette_bibliotheque.png`. Run: `python3 agent/interface_tk.py`; needs `python3-tk` and the `bibliotheque_py` module built in `agent/build/` (the UI adds that folder to `sys.path`).
- 13 pages reached by clicking the sidebar items; the selected item and status bar update on navigation. All pages are wired to `LibrarySession`: books (add, remove by ISBN or selected row, title/author/global search, all/available), users (add/list), loans (borrow/return), live statistics, save and backup (existing `.backup` files are replaced). French success/error messages are shown under the title. Every successful mutation (add/remove book, add user, borrow/return) saves the data files immediately, so changes survive a restart; `session.save()` is also called when the window closes.
- Action buttons are created directly as children of their own frame in `_actions()` (no `pack(in_=...)` from `self.page`), which keeps them visible on every page. `_lire(entree, placeholder)` treats untouched placeholder text as empty input. After a successful user addition, the UI switches to `tous_les_utilisateurs` and shows a confirmation containing the name and ID. Restart the UI after editing `interface_tk.py`; a running Python process does not reload the code.
- `BibliothequeUI(root, data_dir=DONNEES)` accepts another data directory, which is useful for tests; never save into the tracked `agent/data/` while testing.

## Notebooks

- Notebook cwd matters: all data/model paths are relative to the notebook's own directory. Jupyter/VS Code works; running from repo root via nbconvert needs an explicit cwd.
- `apprentissage/`: tracked data and model, so parts can run standalone. Order: `partie1_2.ipynb` (generates tracked `data/dataset.csv` with a leading index column) -> `partie3_entrainement.ipynb` (writes `modele/modele_pokemon.mod`) -> `partie3_predictions.ipynb`.
- `analyse_image/`: `classification.ipynb` -> `test_model.ipynb`. `analyse_image/datas/` is gitignored and untracked; Fashion-MNIST CSVs must be provided locally. The IDX files there are digit MNIST and unused despite the name.
- Tracked `analyse_image/modele/modele.json` + `modele.weights.h5` let `test_model.ipynb` run without training. Re-running `classification.ipynb` overwrites them with Model A only (not the larger Model B).
- Only `analyse_image/requirements.txt` exists (unpinned, 6 packages); notebooks also use `seaborn`, `joblib`, and Pillow. The checked-in `.venv/` is Windows/ignored; recreate it on Linux. `classification.ipynb` uses `ImageDataGenerator`, which current Keras releases have deprecated/removed; AVIF input needs a Pillow build with AVIF support.

## Environment gotchas

- Workspace opened at repo root uses the minimal root `.devcontainer/` (currently untracked); `.vscode/settings.json` hardcodes `cmake.sourceDirectory` to `/workspaces/420-5G4-ML/agent`. The X11/CMake-3.22.2 devcontainer in `agent/.devcontainer/` applies only when `agent/` itself is the VS Code workspace folder.
- Python headers, pip, tkinter and pybind11 were missing for `/usr/bin/python3`; this session installed `python3-dev`, `python3-pip`, `python3-tk` and `python3-venv` via apt and used pybind11 from a temporary venv (`/tmp/opencode/pybind11-venv`, outside the repo). On Debian, PEP 668 blocks `pip install --user`; use a venv or `--break-system-packages`.
- Many tracked files show as modified due to CRLF-only changes (no `.gitattributes`); check real edits with `git diff --ignore-cr-at-eol` before staging.
- Keep French identifiers/messages in the C++ and notebooks; repo docs and code are French.
Verification after writing: re-read this file, run `git diff -- agent/fichiersMD/agents.md`, and confirm no other files were changed (especially no line-ending churn).
