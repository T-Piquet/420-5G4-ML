# HARNESS — working memory for the `agent/` workstream

> **Prime directive.** This file is the single source of truth for how I work on Part 3.
> If reality and this file disagree, reality wins — I fix the file immediately.
> I do not invent scope. When the brief is missing, I ask or I stop.

Revision 4 · 2026-11-17 21:00 (America/New_York) · Owner: `lead`

---

## 0. How this file is used

**Read order at the start of every session:** §1 Mission → §4 Status → §12 Journal.
**Then:** run the Session start ritual, before any edit.

| Trigger | What I update |
|---|---|
| New phase or task | §6 Plan, this revision number |
| Milestone reached | §4 Status, §6 checkboxes, §12 one journal line |
| Real choice made | §8 Decision log (never delete; supersede instead) |
| Surprise / failure | §12 Journal + §10 Risks if it changes the plan |
| End of session | §12 one line: what changed, what is next, what is blocked |

**Status vocabulary:** `TODO` · `WIP` · `DONE` · `WAITING` · `DROPPED`.
**Evidence rule:** any claim about behaviour names the command that proved it. Unverified statements are labelled **assumed**.
**Hygiene:** keep this file under ~350 lines; at a phase boundary, prune stale detail into the journal.

### Session start ritual

```bash
cd /workspaces/420-5G4-ML
git status --short
cmake -S agent -B agent/build -G Ninja >/dev/null && cmake --build agent/build
python3 -m unittest agent.tests.test_store -v
DISPLAY=:0 python3 -m unittest agent.tests.test_gui -v
```

If the build or the tests are red, that is the first task.

---

## 1. Mission

**Confirmed brief.** Replace the numbered TUI menu with the six-screen
**desktop** interface described by the owner's specification, while reading and
writing the same `books.txt` / `users.txt` files.

**Hard constraint from the owner (2026-11-17):** the application must be a
**Python interface app using the C++ core through pybind11** — not a web page,
not a browser app. The HTML mockup is the visual reference, not the delivery
medium.

**Definition of success**

1. A native Python window opens (Tkinter), no server and no browser.
2. The C++ model does the work: `biblio_core` is a pybind11 module built from
   the original `book/user/library/filemanager` sources. Python holds session
   state and draws the interface; it does not reimplement the domain.
3. The six screens and the specification's states exist.
4. Data files keep their exact format; the TUI still builds and runs.
5. Build + tests run from a clean checkout with the documented commands.

**Out of scope:** Parts 1–2 notebooks, the DSH harness checkout, host changes,
new Python packages, web servers, authentication.

---

## 2. Operating context (verified)

| Fact | Value |
|---|---|
| Project root | `/workspaces/420-5G4-ML` |
| Workstream | `/workspaces/420-5G4-ML/agent` |
| C++ | g++ 14.2.0, C++17, `-Wall -Wextra -Wpedantic` |
| Build | CMake 3.22.2, Ninja 1.12.1 |
| Python | 3.13.5, Tkinter 8.6, pybind11 2.13.6 |
| Root access | none (`no-new-privileges`); no Qt/GTK install possible |
| Display | `DISPLAY=:0`, X11 socket mounted; host screen 3840×1080 |
| Window manager | tiles the window to **941×1022** on this host → compact layout required |
| Fonts | DejaVu Sans / DejaVu Serif (design's Inter/Source Serif are not installed; no root) |
| File policy | `danger-full-access`; approvals auto-rejected |

Tkinter is the only native toolkit available without root or pip. The window
manager ignores the requested 1280×860 and tiles to ~941×1022, so the interface
switches to a compact layout below 1120 px (see D12).

---

## 3. Repository map

| Path | What it is |
|---|---|
| `agent/book|user|library|filemanager.*` | Original C++ domain model and persistence |
| `agent/main.cpp` | Original TUI (`bibliotheque` target) |
| `agent/bindings/module.cpp` | pybind11 module `biblio_core` exposing the model |
| `agent/python/store.py` | Session state over `biblio_core` (dirty counters, conflicts, backups); no UI |
| `agent/python/gui.py` | Tkinter window: six screens, dialogs, actions |
| `agent/tests/fixtures/data/` | Reference copy of the seed data (41 / 25, one conflict) |
| `agent/tests/test_store.py` | State + pybind11 tests (headless) |
| `agent/tests/test_gui.py` | Real-window Tkinter tests (needs `DISPLAY`) |
| `agent/docs/specification-gui.md` | Owner's specification (copied verbatim) |
| `agent/docs/mockups/*.html` | Six reference screens (design only, not served) |
| `agent/docs/screenshots/` | Captures of the delivered Tkinter application |
| `agent/run_gui.sh` | Build-if-needed + open the window |
| `build/` (root) | Stale tracked CMake tree, untouched (D2) |

---

## 4. Status (2026-11-17 21:00)

**Build — green.** `cmake -S agent -B agent/build -G Ninja && cmake --build agent/build`
produces `bibliotheque` and `biblio_core.cpython-313-x86_64-linux-gnu.so`, no warnings.

**Tests — green.**

- `python3 -m unittest agent.tests.test_store -v` → **11/11**, including
  `test_uses_pybind11_core`: `isinstance(store.library, biblio_core.Library)`.
- `DISPLAY=:0 python3 -m unittest agent.tests.test_gui -v` → **5/5**: all screens
  build, add/edit/save, loan/return, user creation, backup, quit/delete dialogs.
- Visual pass: native window captured with `xwd` at 941×1022 for dashboard,
  catalogue, book, loans, users; layout defects fixed (sidebar clipping, catalogue
  filters, loan action column, mobile/compact wrapping).

**Running it**

```bash
./agent/run_gui.sh              # opens the Tkinter window, data: agent/data
```

**Not yet done:** owner opens the window once and confirms the result; commit.

---

## 5. Architecture

```
Tkinter window (agent/python/gui.py)
   │  Python calls
   ▼
Store (agent/python/store.py)  — dirty counters, conflicts, backups
   │  pybind11 module
   ▼
biblio_core  (agent/bindings/module.cpp)
   │  C++ calls
   ▼
Library / Book / User / FileManager   ← code shared with the TUI
   ▼
agent/data/books.txt · users.txt
```

Why this shape: the brief mandates pybind11; the container has no root for
Qt/GTK; Tkinter ships with Python and opens a real window on the mounted X11
display. The C++ layer owns the model, search, checkout/return and persistence;
Python owns the session (dirty state, change counts, conflict choices) and the
widgets.

**Bindings exposed:** `Book`, `User`, `Library` (add/remove/find/search/checkout/
return/counts), `FileManager` (load/save/backup). Copy-out helpers return
`std::vector<Book>` / `std::vector<User>` so Python cannot corrupt the core's
ownership.

---

## 6. Plan

| Phase | Goal | Exit criteria | Status |
|---|---|---|---|
| P0 Orientation | Understand TUI, data, environment | Baseline recorded | **DONE** |
| P1 Brief freeze | Turn the attachments into a target | Spec copied, pybind11 + native UI chosen | **DONE** |
| P2 Core & bindings | pybind11 module + session store | Module imports; store tests green | **DONE** |
| P3 Tkinter screens | Six screens + shell + status | All screens build; GUI tests green | **DONE** |
| P4 States & dialogs | Backup/quit/delete/conflict/error/no-data | GUI tests + visual pass | **DONE** |
| P5 Visual pass | Compare with mockup | Captures inspected; layout fixes applied | **DONE** |
| P6 Delivery | Docs, launcher, clean diff, commit | README true, tests green, owner confirms | **WIP** |

### P6 checklist

- [x] `run_gui.sh` launches Tkinter (not the removed web server)
- [x] README rewritten for Tkinter + pybind11
- [x] Web interface and HTTP server removed
- [x] Screenshots replaced with native captures
- [ ] Owner opens `./agent/run_gui.sh` once (P5 acceptance)
- [ ] Commit review / message

---

## 7. Screen acceptance checklist

- [x] **Tableau de bord** — counters, shelf, 7 recent loans + link, inconsistency
      alert, top-5 authors, quick actions, header search.
- [x] **Catalogue** — live accent-insensitive search, three filters with counts,
      compact row layout (title + author + ISBN), status badges, lend/return,
      delete, empty state, "N livres affichés sur 41".
- [x] **Fiche livre / Ajout** — stylised cover, fields, formatted ISBN, borrower
      link, return/edit/delete (disabled while borrowed + explanation), add form
      with validation and duplicate link.
- [x] **Emprunter / Retourner** — two-step selection with filter entries,
      summary bar, confirm, return tab with table.
- [x] **Utilisateurs** — list + detail, initials, loan count, borrowed books with
      return, per-user conflict warning, add form with automatic ID.
- [x] **États** — unsaved banner + Ctrl+S, save toast, backup dialog, quit dialog,
      delete-borrowed dialog, load-time conflict dialog, write-failure banner,
      no-data screen, empty states.

---

## 8. Decision log

| # | Date | Decision | Why |
|---|---|---|---|
| D1 | 2026-11-10 | HARNESS.md at `agent/HARNESS.md`, English, append-only journal | Stable re-entry point |
| D2 | 2026-11-10 | Verify builds out-of-tree / in `agent/build`; leave tracked root `build/` alone | Stale; deleting tracked files is a separate decision |
| D3 | 2026-11-10 | Never test against `agent/data` in place; use a copy/fixture | Tests must not mutate the shipped fixture |
| D4 | 2026-11-18 | ~~C++ + pybind11 + Python stdlib HTTP + web UI~~ **superseded by D11** | Owner requires a non-web interface |
| D5 | 2026-11-18 | No Python dependency beyond the stdlib (Tkinter included) | No pip in the container; reproducible |
| D6 | 2026-11-18 | ~~JSON API returning full state~~ **removed with the web server** | — |
| D7 | 2026-11-18 | Data format untouched; C++ `FileManager` remains the writer | Compatibility with the TUI and fixtures |
| D8 | 2026-11-18 | ~~Bundle Inter/Source Serif~~ **superseded**: use DejaVu (installed) | Tk cannot load woff2; no root to install fonts |
| D9 | 2026-11-18 | Keep the TUI target and `main.cpp` | "Replace the menu", not "delete it" |
| D10 | 2026-11-18 | ~~Headless Chromium for visual checks~~ (web only, historical) | — |
| D11 | 2026-11-17 | **Native Tkinter window**, C++ via pybind11; remove the web app | Owner's explicit requirement; Tk is available without root |
| D12 | 2026-11-17 | Responsive compact layout below 1120 px | The host WM tiles the window to 941 px |
| D13 | 2026-11-17 | Tests use `tests/fixtures/data`, not `agent/data` | The owner's working data may change independently |

---

## 9. Known limitations (deliberate, documented)

1. **Square widgets** — Tk 8.6 has no rounded corners/shadows; the palette,
   typography and hierarchy follow the mockup, not its corner radius.
2. **Fonts** — DejaVu Sans/Serif replace Inter/Source Serif (not installed, no
   root to add fonts; Tk cannot load the woff2 files).
3. **Window tiling** — the host WM forces ~941×1022, hence the compact layout;
   the wide layout is exercised at ≥1120 px on a normal desktop.
4. **"Ignorer" is session-only** — the inconsistency stays in the files and
   returns on restart (as specified).
5. **ISBN pretty-printing** implements the French group-2 ranges and falls back
   to raw digits for other groups.
6. **TUI + GUI concurrently** — no file lock; last save wins.
7. **No native folder chooser** in the no-data screen (Tk has none portable);
   a path field is used.

---

## 10. Risks

| # | Risk | Guardrail |
|---|---|---|
| R1 | Data loss when quitting without saving | Dialog only when dirty; tested |
| R2 | Writing malformed records (`|`, `,`) | Store validation; ISBN normalised |
| R3 | Invariant drift between files | Conflicts computed on every state; repair dialog |
| R4 | Mistaking "tests pass" for "looks right" | Native captures inspected; owner confirm open |
| R5 | Dependency confusion (web leftovers) | Web app removed; README states Tkinter only |
| R6 | Scope creep | No new packages, no Qt, no server |

---

## 11. Definition of done

- [x] Build green, no warnings, from `agent/build`.
- [x] Store tests (11) and GUI tests (5) green.
- [x] `biblio_core` proven to be the C++ pybind11 module in tests.
- [x] README commands are literally true.
- [ ] Owner opened the window and confirmed the visuals.
- [ ] `git diff` reviewed; commit scoped; no build artefacts/temp data.
- [x] HARNESS.md current.

---

## 12. Journal (append-only — newest last)

- **2026-11-10 20:51** — Created this file; TUI baseline, clean build, smoke run.
- **2026-11-10 21:03** — Save round-trip byte-identical; EOF loop and input rules noted.
- **2026-11-18 01:22** — Received the GUI specification and mockup; extracted the
  six screens, design CSS and fonts.
- **2026-11-18 01:39** — First (web) implementation: pybind11 + Python HTTP + JS UI,
  API tests and Chromium/jsdom visual pass. Functional but the wrong delivery medium.
- **2026-11-17 20:44** — Owner: "it shouldn't be a web interface" and "must use
  pybind11". Pivot: keep the pybind11 core, replace the HTTP/JS layer with Tkinter.
- **2026-11-17 20:55** — Extracted `store.py` from the server; built `gui.py` with
  the six screens and dialogs. Fixed 8-digit Tk colours, stale callbacks, compact
  layout, catalogue filters, loan-summary order, book re-render.
- **2026-11-17 21:00** — Removed `agent/web` and the HTTP server; `run_gui.sh` now
  opens the Tk window. Tests split into `test_store` (11, pybind11 identity) and
  `test_gui` (5, real window). Native screenshots replace the web captures.

---

## 13. Open questions

| # | Question | Why it matters |
|---|---|---|
| Q1 | Does the native window match what you intended? | Final acceptance; I can adjust spacing/labels |
| Q2 | Commit the work now (and which parts: mockups/screenshots)? | Repository state |
| Q3 | Keep the TUI target alongside the GUI, or remove `main.cpp`? | Currently kept (D9) |
| Q4 | Should `agent/data` be restored to the tracked seed? | It currently holds a resolved-conflict variant; tests use the fixture |
