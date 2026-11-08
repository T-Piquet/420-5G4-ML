# Agent Guidance: Bibliotheque Library System (C++ CMake Project)

## Build & Run

**Build:**
```bash
mkdir build && cd build && cmake .. && make
```

**Run:**
- Default data dir: `./bibliotheque`
- Custom data dir: `./bibliotheque -d <path>` (e.g., `-d ./data`)

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `agent/` | C++ source code for library management system |
| `python_bindings/` | Python wrapper using pybind11 |
| `data/` | Sample data files (`books.txt`, `users.txt`) |
| `ollama/` | Local LLM configuration (Modelfile) |

## Data Format

**Location:** `{data_dir}/books.txt` and `{data_dir}/users.txt`

**Format:** Pipe-separated values
- `books.txt`: `id|title|isbn|author|year`
- `users.txt`: `id|name|email,borrowed_isbn1, borrowed_isbn2`

## CMake Configuration

```cmake
cmake_minimum_required(VERSION 3.21)
project(bibliotheque)
file(GLOB SOURCES "*.cpp")
add_executable(${PROJECT_NAME} ${SOURCES})

# C++17 required
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# Enable all warnings
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
```

## Source Modules

- `main.cpp`: Interactive menu-driven application entry point
- `library.*`: Data model and business logic (books, users, borrowing)
- `book.*`: Book CRUD operations and entity representation
- `user.*`: User CRUD operations and entity representation
- `filemanager.*`: File I/O for persisting data to disk

## Python Bindings

Build and use the Python wrapper via `python_bindings/`. See `setup.py` for installation and `examples/bibliotheque_usage.py` for usage patterns.

## Dev Container Notes

- X11 forwarding enabled for GUI tools
