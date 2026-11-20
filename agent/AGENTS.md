# AGENTS.md

French-language coursework repo ("Atelier ML") with three independent parts.
Keep UI text, identifiers, and comments in French.

## Layout
- `agent/` — C++17 console app `bibliotheque` (personal library manager).
  Entrypoint `main.cpp`; core in `library.*`, `filemanager.*`, `book.*`, `user.*`.
- `apprentissage/` — Pokémon win-rate regression notebooks (pandas/scikit-learn/joblib).
- `analyse_image/` — fashion-MNIST CNN notebooks (Keras/TensorFlow) + saved model.

No tests, linter, CI, or root package manifest.

## agent (C++)
```bash
cd agent
cmake -S . -B build
cmake --build build
./build/bibliotheque -d data
```
- Always pass `-d/--data-dir`; without it the data paths are empty and nothing loads or saves.
- `CMakeLists.txt` globs `*.cpp` at configure time: re-run the configure step after adding/removing a source file.
- `-Wall -Wextra -Wpedantic` are enabled but not errors; keep the build warning-free.
- `data/books.txt` (`title|author|isbn|available(0/1)|borrowerId`) and
  `data/users.txt` (`name|userId|isbn1,isbn2`) are tracked fixtures that the app
  overwrites on save/exit (menus 12, 13, 0). Expect diffs when smoke-testing.
- `fromFileFormat`/`toFileFormat` in `book.cpp` and `user.cpp` are the
  authoritative on-disk format.

## Notebooks
- Run Jupyter from inside each notebook's own directory; all paths are relative
  (`datas/...`, `modele/...`).
- `apprentissage` pipeline order: `partie1_2.ipynb` (cleans `pokedex.csv`, writes
  tab-separated `datas/dataset.csv`) → `partie3_entrainement.ipynb` (writes
  `modele/modele_pokemon.mod`) → `partie3_predictions.ipynb`.
  `datas/dataset.csv` is committed even though it is generated.
- `analyse_image/classification.ipynb` needs `datas/fashion-mnist_train.csv` and
  `datas/fashion-mnist_test.csv`, which are gitignored (~133 MB / 22 MB) and not
  present in a fresh clone; download them before running.
- The image model is stored as `modele/modele.json` + `modele/modele.weights.h5`;
  load with `model_from_json` + `load_weights`, not `load_model`.
- No dependency manifest exists, and the root `.venv/` is stale (created under
  `/home/youssef`, `pip` broken, no sklearn/TensorFlow). Create a fresh
  environment. Needed: numpy, pandas, scikit-learn, joblib, matplotlib, seaborn;
  tensorflow/keras and pillow for `analyse_image`.
- `.vscode/settings.json` points CMake at a nonexistent absolute
  `/home/youssef/...` path; ignore it or fix it locally.
