# AGENTS.md

Atelier ML (school lab) with three independent parts, all under `agent/`. The root `README.md` is stale: it says `apprentissage/` and `analyse_image/` at the root, but the real paths are `agent/apprentissage/` and `agent/analyse_image/`.

## C++ CLI (`agent/`)

Build (CMake ≥ 3.21, C++17):
```bash
cd agent
mkdir -p build && cd build
cmake .. && make -j
```

Run from `agent/build`, pointing at a data dir:
```bash
./bibliotheque -d ../data       # also --data-dir
```

- `CMakeLists.txt` globs `agent/*.cpp` into one `bibliotheque` executable. Do not add a second `main()`; after adding/removing a `.cpp`, re-run `cmake ..` because the glob is only evaluated at configure time.
- No tests, lint config, or CI. Compilation uses `-Wall -Wextra -Wpedantic`, so new code should build warning-free.
- Data files are pipe-separated: `books.txt` = `title|author|isbn|available(1/0)|borrowerId`, `users.txt` = `name|userId|isbn,isbn`.
- Without `-d`, file names are empty and nothing loads/saves. With `-d`, the app **rewrites the tracked fixture files on exit**; test against a temp copy of `agent/data` if you add books/users.
- UI text and docs are French; C++ comments are English.
- `.devcontainer/` (inside `agent/`) mounts the X11 socket with `--net=host` and forwards `DISPLAY` for Tk windows. `.vscode/settings.json` hardcodes a Windows CMake source path; ignore or repoint it to `agent`.

## Notebooks

Always start Jupyter in the notebook's own directory; all paths are relative to it.

- `agent/apprentissage/`: reads `../data/pokedex.csv` / `../data/combats.csv`, writes `modele/` artifacts.
- `agent/analyse_image/`: reads `datas/…` and `modele/…`.

Required order for the learning part: `partie1_2.ipynb` builds `agent/data/dataset.csv` (tab-separated) → `partie3_entrainement.ipynb` trains and overwrites `agent/apprentissage/modele/modele_pokemon.mod` → `partie3_predictions.ipynb` loads that model.

- `agent/data/dataset.csv` and both model artifacts are tracked, but generated. Retraining silently rewrites committed files, including a multi-MB `.mod` and `.weights.h5`.
- `agent/analyse_image/datas/` is gitignored (~200 MB of Fashion-MNIST CSVs/IDX files); a fresh clone lacks them, so `classification.ipynb` cannot run until the data is supplied.
- `classification.ipynb` forces CPU via `tf.config.set_visible_devices([], 'GPU')`.
- Python is 3.13. No lockfile/requirements: pandas, numpy, matplotlib, seaborn, scikit-learn, joblib, tensorflow/keras, pillow. The devcontainer installs none of the ML packages.
