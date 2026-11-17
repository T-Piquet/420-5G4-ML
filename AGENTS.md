# AGENTS.md

## Layout
Three independent exercises; there is no root build, test runner, CI, or package manifest.
- `agent/` — C++17 CLI `bibliotheque` (personal library manager), CMake.
- `apprentissage/` — scikit-learn notebooks (Pokémon battle prediction).
- `analyse_image/` — TensorFlow/Keras notebooks (Fashion-MNIST CNN).

Docs, UI strings, comments, and commit messages are in French; keep that convention.

## agent/ (C++)
- Build: `cmake -S agent -B agent/build && cmake --build agent/build`
  (binary: `agent/build/bibliotheque`).
- `CMakeLists.txt` uses `file(GLOB *.cpp)`: re-run CMake after adding/removing a source file, otherwise the new file is not compiled.
- Run with a data directory: `cd agent && ./build/bibliotheque -d data`.
  Without `-d`, file paths are empty and loading/saving fails.
- The app writes `books.txt`/`users.txt` in place; menu 13 also creates `*.backup`. Test against a copy (e.g. `cp -r agent/data /tmp/libdata`) so tracked sample data stays clean.
- On-disk format is `|`-separated:
  - books: `title|author|isbn|1|borrowerId` (`1` available, `0` checked out)
  - users: `name|userId|isbn1,isbn2`
- No tests. Verification = warning-free build (`-Wall -Wextra -Wpedantic`) plus a manual CLI run.

## Notebooks
- Run notebooks with the working directory set to their own folder (`apprentissage/` or `analyse_image/`); every data/model path is relative.
- `apprentissage/`: `datas/dataset.csv` is tab-separated (`delimiter='\t'`). The model is persisted with joblib as `modele/modele_pokemon.mod` (the extension does not indicate the real format).
- `analyse_image/`: the model is a Keras JSON architecture (`modele/modele.json`) plus weights (`modele/modele.weights.h5`), loaded via `model_from_json` + `load_weights`. `test_model.ipynb` expects `images/sandale.jpg`.
- `analyse_image/datas/fashion-mnist_{train,test}.csv` are gitignored and untracked; a fresh clone only has the `.idx*-ubyte` files, so `classification.ipynb` needs those CSVs regenerated or obtained first.
- No requirements file. Install manually: pandas, numpy, matplotlib, seaborn, scikit-learn, joblib, tensorflow/keras, Pillow. The devcontainer preinstalls only pybind11, tk, and venv.

## Git
- Commit messages use French tags such as `[TACHE]`, `[FIX]`, `[REMISE]`.
- `agent/build/` is ignored. Large datasets and models under `*/datas/` and `*/modele/` are tracked; do not delete them.
