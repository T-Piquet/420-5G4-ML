# AGENTS.md

## Project Overview
This repository contains a C++17 personal library management system (**Bibliothèque**) developed for coursework (`420-5G4-ATML`), paired with a `pybind11` C++ bridge and a Python `customtkinter` graphical user interface (GUI) for managing books, library users, checkouts/returns, statistics, and text-file persistence.

## Project Structure
- `main.cpp`: Interactive CLI menu loop, argument parsing (`--data-dir` / `-d`).
- `book.h` / `book.cpp`: Book entity model (title, author, ISBN, availability, borrower tracking).
- `user.h` / `user.cpp`: User entity model (name, user ID, list of borrowed book ISBNs).
- `library.h` / `library.cpp`: In-memory business logic and repository container managing books, users, search, checkouts/returns, and statistics.
- `filemanager.h` / `filemanager.cpp`: Persistence layer reading/writing formatted text files (`books.txt`, `users.txt`) and creating `.backup` files.
- `bindings/bindings.cpp`: `pybind11` C++ module (`bibliotheque_cpp`) exposing `Book`, `User`, `Library`, and `FileManager` to Python.
- `gui/`: Python `customtkinter` application:
  - `app.py`: GUI entry point (`AppShell`).
  - `bibliotheque_api.py`: Python facade (`BibliothequeAPI`) wrapping `bibliotheque_cpp` (with a Python file-backed fallback when the C++ module is not compiled).
  - `theme.py`: Color, corner-radius, and font tokens.
  - `requirements.txt`: Python dependencies (`customtkinter>=5.2.0`).
  - `ui/`: `shell.py`, `nav_bar.py`, `table.py`, `widgets.py`, `icons.py`, and `pages/` (`base.py`, `books.py`, `users.py`, `settings.py`, `Stats.py`).
- `tests/test_bridge.py`: Integration tests for `BibliothequeAPI` and the `pybind11` bridge.
- `data/`: Sample datasets (`books.txt`, `users.txt`).
- `Maquette/`: UI design mockups (`Page Livre.png`, `Page Membre.png`, `Page pret.png`, `Page stat.png`).
- `CMakeLists.txt`: CMake build configuration targeting C++17 (`bibliotheque` CLI executable and `bibliotheque_cpp` `pybind11` shared module output to `gui/`).
- `.devcontainer/`: VS Code development container configuration (GCC, CMake, `pybind11`, `python3-tk`, Ollama, OpenCode).

## Build and Run

### Prerequisites
- C++17 compliant compiler (`g++`, `clang++`, or MSVC)
- CMake 3.21+ and Make / Ninja
- Python 3 with `pybind11` (`python3-pybind11`, `pybind11-dev`) and `customtkinter`

### Build C++ CLI & `pybind11` Module
```bash
cd agent
mkdir -p build && cd build
cmake ..
make
```
This builds `./bibliotheque` and outputs `bibliotheque_cpp*.so` into `agent/gui/`.

### Run the C++ CLI
```bash
./bibliotheque -d ../data
# or
./bibliotheque --data-dir ../data
```

### Run the Python GUI
```bash
cd agent/gui
python3 -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python3 app.py              # Windows: python app.py
```

### Run Tests
```bash
python3 agent/tests/test_bridge.py
```

## Conventions & Standards
- **Standard**: C++17 (`CXX_STANDARD 17`, extensions disabled).
- **Warnings**: Clean compile with `-Wall -Wextra -Wpedantic`.
- **Memory Management**: Modern C++ idioms using standard containers (`std::vector`) and smart pointers (`std::unique_ptr`). Raw pointers returned by lookup methods represent non-owning references (`py::return_value_policy::reference_internal` in `pybind11`).
- **Language**: User interface and console prompts are in French; identifiers, class members, and code logic are in English.
