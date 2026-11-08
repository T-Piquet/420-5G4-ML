# AGENTS.md

Bibliothèque is a personal library manager: a C++17 core with two front ends, an interactive terminal menu and a Python/customtkinter GUI that calls the core through pybind11.

Run every command below from `agent/`, which is a subfolder of the `420-5G4-ML` course repository. User-facing text, including CLI output and GUI messages, is in French.

## Commands

```bash
# Terminal app
cmake -S . -B build/cli && cmake --build build/cli
./build/cli/bibliotheque -d <data_dir>

# C++ module used by the GUI
cmake -S python_bindings -B build/python_bindings
cmake --build build/python_bindings

# GUI (needs an X11 display, forwarded by the dev container)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py -d data
```

There is no test suite, linter or formatter. C++ targets compile with `-Wall -Wextra -Wpedantic`, so check changes by building both targets and keeping the output free of warnings.

## Architecture

```
main.cpp (terminal menu) ───────────────────────┐
                                                ├─> Library, Book, User, FileManager
main.py > gui/ (MVC) > python_bindings.cpp ─────┘             (C++ core)
```

- **Core:** `Library` owns the books and users. `FileManager` reads and writes the text files. `main.cpp` is not part of the Python module, so shared behaviour belongs in the core.
- **Loans are stored twice:** `Book` holds the availability flag and borrower ID, and `User` holds the borrowed ISBNs. Use `Library::checkOutBook` and `Library::returnBook`, which update both sides.
- **Bindings:** `python_bindings.cpp` exposes snake_case names. Lists and lookups return copies, so changing a returned `Book` or `User` does not change the library. All state changes must go through `Library` methods.
- **GUI model:** `gui/models/backend.py` imports the compiled module from `build/python_bindings/`. `LibraryModel` is the only class that calls it, and it converts results to the dataclasses in `entities.py`.
- **Validation:** `Library` does not check for duplicates or forbidden characters. For the GUI, `LibraryModel` does this and raises `LibraryError`, whose message is shown directly to the user, so write it in French.
- **GUI refresh:** Each model change calls `_mark_changed()`, which notifies `AppController`, which refreshes the current page. Views expose callbacks and do not access the model. Controllers connect the two.

`gui/_legacy/` is not imported by the current GUI. `chatLogs/` contains exported agent sessions.

## Data files

`<data_dir>/books.txt` and `<data_dir>/users.txt` use `|` as a separator, with no header and no escaping:

```
books.txt: title|author|isbn|available(1 or 0)|borrower_id
users.txt: name|user_id|isbn1,isbn2
```

A `|` or newline in a field corrupts its line, and so does a `,` in an ISBN list entry.

## Pitfalls

- **Use a copy of the data when testing the CLI:** choosing `0` to quit saves automatically, which overwrites the files in `<data_dir>`. The GUI saves only on request (`Ctrl+S` or the save prompt on close).
- **Always pass `-d` to the CLI:** without it, the file paths are empty, so the app starts with an empty library and cannot save.
- **Rebuild after C++ changes:** the GUI loads the compiled `.so` from `build/python_bindings/`, so it keeps running the old code until the module is rebuilt.
- **Exposing a new core feature to the GUI** takes three changes: the C++ method, its binding in `python_bindings.cpp`, and a `LibraryModel` method that calls `_mark_changed()` if it modifies state.
- **Adding a `.cpp` file to the core:** the root `CMakeLists.txt` uses a glob, so re-run CMake configure. `python_bindings/CMakeLists.txt` and `python_bindings/setup.py` list sources by hand, so add it to both.
- **Python versions must match:** the `.so` is built for the Python that CMake finds, which must be the same version as the one in `.venv`.

## Environment

The dev container (`.devcontainer/`).