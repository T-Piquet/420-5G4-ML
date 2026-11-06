# Atelier ML — Yassine Satrallah (2384062)

Ce dépôt regroupe les trois parties de l'atelier du cours
**420-5G4 — Atelier ML**.

## Contenu du dépôt

| Partie | Dossier | Sujet |
| --- | --- | --- |
| **1** | `apprentissage/` | Régression du taux de victoire Pokémon avec scikit-learn |
| **2** | `analyse_image/` | Classification d'images Fashion-MNIST avec TensorFlow/Keras |
| **3** | `agent/` | Bibliothèque en C++17, bindings pybind11 et interface CustomTkinter |

---

## Partie 3 — Bibliothèque personnelle (C++ / pybind11 / CustomTkinter)

Cette partie contient :

- le cœur métier en **C++17** (`Book`, `User`, `Library`, `FileManager`) ;
- le module Python **`bibliotheque_cpp`** exposé avec **pybind11** ;
- une **interface graphique en français** réalisée avec **CustomTkinter** ;
- une **sauvegarde automatique** après chaque modification ;
- des **tests autonomes** pour les bindings et les mutations.

### Démarrage rapide depuis le devcontainer

Le devcontainer se trouve dans `agent/.devcontainer`. Il installe CMake,
le compilateur C++, pybind11, Tkinter, CustomTkinter et un bureau graphique
accessible via **noVNC** sur le port **6080**.

1. **Ouvrir le dossier `agent/`** dans VS Code (et non la racine du dépôt) :

   ```bash
   code /chemin/vers/le-depot/agent
   ```

   > Le dossier `agent/` doit être la racine ouverte dans VS Code, car c'est
   > lui qui contient `.devcontainer/`.

2. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**, puis attendre la
   fin de la construction.

3. Dans un terminal du conteneur, compiler :

   ```bash
   cmake -S . -B build -DPython_EXECUTABLE=$(which python3)
   cmake --build build
   ```

4. Vérifier l'installation :

   ```bash
   PYTHONPATH=build python3 tests/test_bindings.py
   PYTHONPATH=build python3 tests/test_service.py
   ```

5. Lancer l'interface graphique :

   ```bash
   PYTHONPATH=build python3 gui/app.py --data-dir data
   ```

   Ouvrir ensuite **http://localhost:6080** (ou l'onglet **Ports** de VS Code)
   et utiliser le mot de passe **`vscode`**.

> **Guide détaillé, structure du projet, format des données et dépannage :**
> [`agent/README.md`](agent/README.md)

---

## Partie 1 — Régression Pokémon

```bash
cd apprentissage
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ouvrir les notebooks dans l'ordre :

1. `partie1_2.ipynb` — construit `data/dataset.csv` à partir de `pokedex.csv`
   et `combats.csv` ;
2. `partie3_entrainement.ipynb` — entraîne les modèles et écrit
   `modele/modele_pokemon.mod` ;
3. `partie3_predictions.ipynb` — charge le modèle et effectue des prédictions.

> Exécuter les cellules de haut en bas et depuis le dossier `apprentissage/`
> (les chemins sont relatifs).

---

## Partie 2 — Classification Fashion-MNIST

```bash
cd analyse_image
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Télécharger `fashion-mnist_train.csv` et `fashion-mnist_test.csv` (par exemple
depuis [Kaggle — Fashion MNIST](https://www.kaggle.com/datasets/zalando-research/fashionmnist))
dans `analyse_image/data/`, puis exécuter `classification.ipynb`.

> Ces deux fichiers ne sont pas versionnés (volumineux) : ils doivent être
> téléchargés avant l'exécution.

> L'entraînement force le CPU et peut être long (50 epochs pour la version
> augmentée). Les modèles entraînés sont déjà présents dans `modele/`.

---

## Remarques

- Les dépendances Python de chaque partie sont installées dans un
  environnement virtuel local (`.venv`), non versionné.
- Le dossier `agent/build/` est généré par CMake et ignoré par Git.
- Les données d'exemple de la partie 3 sont dans `agent/data/`.
