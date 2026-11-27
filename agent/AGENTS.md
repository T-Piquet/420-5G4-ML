# AGENTS.md — agent/

C++17/CMake console app plus a Python/customtkinter UI in `ui/`. The rest of the
repo (`apprentissage/`, `analyseimage/`) is separate Python/ML coursework — only
touch `agent/` unless asked.

## Build & run

```bash
cd agent
cmake -S . -B build
cmake --build build -j
./build/bibliotheque -d data
```

- Binary is `bibliotheque`.
- `CMakeLists.txt` globs `*.cpp`: after adding/removing a source, re-run the
  `cmake -S . -B build` configure step. A plain rebuild will not pick it up.
- `-d/--data-dir` is required for persistence. Without it both data filenames are
  `""`, so loading silently does nothing and saving fails. Run from `agent/` so
  `-d data` resolves.
- No tests, linter, or formatter. Verification = a clean build; warnings are on
  (`-Wall -Wextra -Wpedantic`, C++17, no extensions).
- Menu is interactive stdin. Smoke-test with piped input, e.g.
  `printf '0\n' | ./build/bibliotheque -d data`.

## Layout

- `main.cpp` — CLI arg parsing and the menu loop; all UI text is French.
- `library.*` — in-memory store (`unique_ptr<Book/User>`), search, loan, stats.
- `filemanager.*` — pipe-separated persistence plus `.backup` copies.
- `book.*`, `user.*` — models and their (de)serialization.
- `data/` — sample fixtures (42 books, 25 users) used with `-d data`.

## Data format (when editing fixtures directly)

- `books.txt`: `title|author|isbn|available|borrowerId` (`1`/`0`; borrowerId
  empty when available).
- `users.txt`: `name|userId|isbn1,isbn2,...`.
- Keep them consistent: a checked-out book's `borrowerId` must match a user
  whose borrowed list contains that ISBN.

## Python UI (`ui/`)

Minimal customtkinter window. `customtkinter` is not installed system-wide; use
the project venv.

```bash
cd agent/ui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

- Entry point `app.py`, window class in `main_window.py`.
- Needs X11 (`DISPLAY` + mounted X socket, provided by the devcontainer).
- Headless-safe smoke test: `MainWindow()`, `app.after(500, app.destroy)`, `app.mainloop()`.

## Gotchas

- Root `.vscode/settings.json` hardcodes `/home/raphael/...`; don't rely on it.
- Git commit messages are French with a bracketed tag prefix (`[CREATE]`,
  `[REMISE]`).
