# Repository guide

## C++ library CLI (`agent/`)

- From the repo root: `cmake -S agent -B agent/build && cmake --build agent/build`. CMake 3.21+ builds the C++17 `bibliotheque` executable from `agent/main.cpp` and the other top-level `.cpp` files. The checked-in VS Code CMake setting points to a machine-specific absolute path; use the explicit `-S agent` command.
- There are no CTest targets. For a smoke test, copy `agent/data/` to a scratch directory, then run `./agent/build/bibliotheque -d <scratch-data-dir>` and enter `0` to exit. Even a normal exit rewrites `books.txt` and `users.txt`, so don't point `-d` at the tracked fixtures. The CLI does not need the devcontainer's X11 forwarding.

## CustomTkinter GUI (`agent/`)

- Use the `agent/` devcontainer with Python development headers, Tk, `venv`, and pybind11 installed. The container must have access to a display server (for example, through X11 forwarding).
- Run these commands from the repository root. Use a scratch copy of `agent/data/` for all borrowing, return, and save tests; quitting the GUI also saves the data.

  ```sh
  work="$(mktemp -d)"
  python3 -m venv "$work/venv"
  py="$work/venv/bin/python"
  "$py" -m pip install -r agent/requirements-gui.txt
  cmake -S agent -B "$work/build" -DBIBLIOTHEQUE_BUILD_PYTHON=ON -DPython_EXECUTABLE="$py"
  cmake --build "$work/build" --target _bibliotheque
  cp -R agent/data "$work/data"
  PYTHONPATH="$work/build" "$py" agent/gui.py --data-dir "$work/data"
  ```

- Persistence smoke test: select **Le Petit Prince** (ISBN `9782070612758`) in **Catalogue**, click **Emprunter**, and enter `USR001`. In **Sauvegardes**, click **Sauvegarder les données**, then quit and repeat only the launch command with the same scratch directory. In **Tous les livres**, confirm that the book shows **Emprunté par : Marie Dubois**; it should not appear in **Livres disponibles**.

## ML notebooks

- Start each kernel in its notebook's directory: paths such as `data/`, `modele/`, and `images/` are relative to the working directory. There is no tracked Python dependency manifest; the ignored `apprentissage/.venv/` is local setup.
- In `apprentissage/`, `partie3_predictions.ipynb` loads the tracked `modele/modele_pokemon.mod` written by `partie3_entrainement.ipynb`. The training notebook reads `data/dataset.csv` as tab-separated despite its extension.
- In `analyse_image/`, `test_model.ipynb` runs inference using the tracked model JSON and `.weights.h5` plus sample images. It can run without retraining; `classification.ipynb` needs the Fashion-MNIST train and test CSVs under the ignored `analyse_image/data/` and can overwrite the tracked model files.
