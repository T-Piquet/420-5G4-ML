# AGENTS.md

- Three unrelated parts, no root build/test harness: `apprentissage/` (Pokémon notebooks), `analyse_image/` (Fashion-MNIST notebooks/model), `agent/` (C++17 library CLI). Root `README.md` is only a directory map.
- C++ build/run from `agent/`: `cmake -S . -B build && cmake --build build && ./build/bibliotheque -d data`. Without `-d/--data-dir`, paths stay empty, so the app starts empty and saving fails.
- `agent/CMakeLists.txt` globs all `agent/*.cpp`; adding a `.cpp` with another `main()` breaks the single `bibliotheque` target. No tests/CTest/lint targets exist.
- CLI is interactive; quitting with `0` auto-saves. `13` copies data to `.backup` via `copy_file` and will fail if the backup already exists. Data files are pipe-separated (`title|author|isbn|available|borrowerId`).
- `agent/.devcontainer` mounts X11 with `--net=host`; image installs CMake 3.22.2 via `reinstall-cmake.sh`. Project requires CMake >= 3.21; warnings use `-Wall -Wextra -Wpedantic` (not `-Werror`).
- Notebooks must run with the notebook's directory as cwd: `apprentissage/` uses `../data/...`, `analyse_image/` uses `datas/...` and writes `modele/...`.
- No Python dependency manifest; use the ignored root `.venv/` if present. `analyse_image/datas/*.csv` are gitignored (only `.idx` files are tracked), so a fresh clone lacks those CSVs. Notebooks need pandas/numpy/matplotlib; `analyse_image/` also needs TensorFlow/Keras.
- User-facing strings and comments are mostly French; keep that convention when editing CLI/notebook code.
