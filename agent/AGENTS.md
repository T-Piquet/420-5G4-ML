# AGENTS.md

School assignment (420-5G4 ML) with three independent parts. Notebook prose and all CLI/user-facing text are French — keep new text and comments in French.

## Layout

- `apprentissage/` — Pokémon win-rate regression (scikit-learn). `partie1_2.ipynb` builds `data/dataset.csv`; `partie3_entrainement.ipynb` trains and writes `modele/modele_pokemon.mod`; `partie3_predictions.ipynb` loads that model.
- `analyse_image/` — Fashion-MNIST CNN (TensorFlow/Keras). `classification.ipynb` trains and writes `modele/modele.json` + `modele/modele.weights.h5`; `test_model.ipynb` is empty.
- `agent/` — C++17 library CLI (`bibliotheque`) plus a devcontainer for the GUI/agent phase. `agent/opencode.json` points the Ollama provider at the host (`host.docker.internal:11434`).
- `agent/gui/` — CustomTkinter GUI (J4, mutations + auto-save): `app.py` entry point, `service.py` snapshots/mutations, `views/`, `components/` (dialogs, banner, table, status). Run `python3 gui/app.py --data-dir data`.

Phase 2 has standalone `agent/tests/test_bindings.py` (bindings) and `agent/tests/test_service.py` (mutations/auto-save), no pytest; there is no lint or CI setup.

## Commands

Python (each part has its own uncommitted `.venv`; run notebooks with that directory as the working directory because paths are relative):

```bash
cd apprentissage        # or analyse_image
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

C++ — use the devcontainer (`agent/.devcontainer/`), which installs cmake, pybind11, Tkinter, and customtkinter:

```bash
cd agent
cmake -S . -B build
cmake --build build
./build/bibliotheque -d data
```

`-d/--data-dir` is effectively required: without it `FileManager` opens empty filenames and saving fails. `agent/build/` is gitignored. `agent/bindings.cpp` builds the `bibliotheque_cpp` module; CMake fails at configure time if pybind11 is missing.

## Gotchas

- `apprentissage/partie1_2.ipynb` must run before training: it writes the tab-separated `data/dataset.csv` from `pokedex.csv` + `combats.csv` (and patches the missing name for Pokémon #63).
- In `partie3_entrainement.ipynb`, run cells top to bottom. The early `y = dataset.iloc[:, 17]` is overridden by `y = dataset.iloc[:, 16]` in the train/test-split cell; the models use column 16. Training reads `dataset.csv` with `delimiter='\t'`.
- `analyse_image/data/` is gitignored. Download `fashion-mnist_train.csv` and `fashion-mnist_test.csv` there before running `classification.ipynb`.
- Image training forces CPU (`tf.config.set_visible_devices([], 'GPU')`), and the augmented run is 50 epochs — slow and expensive.
- Trained artifacts are committed (`apprentissage/modele/modele_pokemon.mod`, `analyse_image/modele/*`); rerunning training overwrites them.
- Agent data files are pipe-delimited, one record per line: `books.txt` = `title|author|isbn|1/0|borrowerId`, `users.txt` = `name|userId|isbn,isbn`.
- `agent/chatsLogs/` holds `/export` output; leave its `.gitkeep` in place.
- The devcontainer exposes the desktop GUI on forwarded port 6080 (noVNC).

## Phase 2 roadmap — pybind11 + customtkinter

Goal: keep the `bibliotheque` CLI target and add a French GUI on top of a `bibliotheque_cpp` module. Decisions: auto-save after every mutation; default data dir `agent/data`, overridable with `--data-dir`; standalone assert-based test script (no pytest).

### Binding surface (`agent/bindings.cpp`)

- Expose `Book`, `User`, `Library`, `FileManager`; include `<pybind11/stl.h>`.
- `Book`: both constructors, getters/setters, `checkOut`, `returnBook`, `toString`, `toFileFormat`, `fromFileFormat`.
- `User`: both constructors, getters/setters, `borrowBook`, `returnBook`, `hasBorrowedBook`, `getNumberOfBorrowedBooks`, `getBorrowedBooks`, `toString`, `toFileFormat`, `fromFileFormat`.
- `Library`: `addBook`, `removeBook`, `findBookByISBN`, `searchBooksByTitle`, `searchBooksByAuthor`, `getAvailableBooks`, `getAllBooks`, `addUser`, `findUserById`, `getAllUsers`, `checkOutBook`, `returnBook`, stats getters. Skip `display*` (stdout) for the GUI.
- `FileManager`: constructor, `saveLibraryData`, `loadLibraryData`, `createBackup`, `fileExists`; individual load/save only if needed.
- `Library` owns `unique_ptr`: never expose its copy. Use `reference_internal` for raw-pointer returns; prefer copy-returning wrappers (`std::vector<Book>`, `std::optional<Book>`) for collection reads so Python snapshots cannot dangle after `removeBook`.
- `FileManager::loadLibraryData` appends: load into a fresh `Library` every time. `createBackup` throws if a `.backup` already exists. `addBook`/`addUser` allow duplicates and `removeBook` allows deleting a borrowed book — enforce those rules in the Python service.
- C++ search uses byte-wise `::tolower`; filter accented French text in Python instead.

### Milestones

1. **J1 — module build**: add `bindings.cpp`; make CMake fail loudly if `bindings.cpp` exists but pybind11 is missing; build and import `bibliotheque_cpp`.
   Verify: `PYTHONPATH=build python3 -c "import bibliotheque_cpp as b; print(b.Library())"`.
2. **J2 — binding/persistence test**: `agent/tests/test_bindings.py` using a temp data dir; cover constructors, search, checkout/return, save/load round-trip, backup, and error cases.
   Verify: `PYTHONPATH=build python3 tests/test_bindings.py` exits 0 and does not touch `agent/data`.
3. **J3 — GUI shell**: `agent/gui/` with `app.py`, `service.py`, `views/` (dashboard, catalogue, users, loans), `components/` (dialogs, table, status). French labels, sidebar navigation, read-only data first.
   Verify: launch under noVNC (port 6080); every view renders without traceback.
4. **J4 — wiring + errors**: connect the service to C++, auto-save after mutations, validation, confirmations, notifications, backup. Manual scenario: add book/user, checkout/return, delete, restart, data persists.
   Verify: invalid inputs and deleting a borrowed book are blocked with a French message.

### Build/run commands

```bash
cd agent
# devcontainer: customtkinter is preinstalled; otherwise activate a venv first
# python3 -m pip install customtkinter pybind11
cmake -S . -B build -DPython_EXECUTABLE=$(which python3)
cmake --build build
PYTHONPATH=build python3 tests/test_bindings.py
PYTHONPATH=build python3 tests/test_service.py
PYTHONPATH=build python3 gui/app.py --data-dir data
```

If CMake cannot find pip's pybind11: add `-Dpybind11_DIR=$(python3 -m pybind11 --cmakedir)`.

### Acceptance checks

- Module built for the same interpreter that runs the GUI (`import` succeeds, no ABI/version mismatch).
- Persistence round-trip via a fresh `Library`; no duplicate records after reload.
- GUI runs in the devcontainer; CLI `bibliotheque -d data` still works.
- After tests, `git status` shows no generated `.so`, `build/`, or modified `data/*.txt`.
