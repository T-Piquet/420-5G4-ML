# Bibliothèque — interface graphique Python

Application de gestion de bibliothèque : le cœur métier est écrit en C++17
(`book`, `user`, `library`, `filemanager`) et exposé à Python via pybind11.
L'interface graphique utilise customtkinter.

## Prérequis

- CMake 3.21 ou plus récent et un compilateur C++17.
- Python 3.9 ou plus récent (le module pybind11 doit être compilé avec le même
  interpréteur que celui qui lance la GUI).
- Sous Windows/WSL, un serveur X (WSLg, ou VcXsrv/XLaunch).

## Compiler le cœur C++ et le module Python

Depuis le dossier `agent/` :

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r python/requirements.txt

mkdir -p build
cd build
cmake ..
make
```

Sous Windows (PowerShell), l'activation du venv est différente :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r python\requirements.txt

mkdir build
cd build
cmake ..
cmake --build . --config Release
```

Le module Python est produit dans `build/`
(`bibliotheque_py*.so` sous Linux, `bibliotheque_py*.pyd` sous Windows).
Relancer `cmake ..` après avoir ajouté ou renommé un fichier source.

## Afficher la GUI depuis WSL

### WSLg (Windows 11)

WSLg fonctionne sans configuration : lancer directement la commande ci-dessous.

### VcXsrv / XLaunch

1. Installer VcXsrv sur Windows et lancer **XLaunch**.
2. Choisir **Multiple windows**, numéro d'affichage `0`.
3. Choisir **Start no client**, cocher **Disable access control**, puis terminer.
4. Dans le terminal WSL, exporter l'affichage :

```sh
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0.0
```

## Lancer la GUI

Depuis `agent/`, avec le venv activé :

```sh
python python/app.py
```

Sous Windows natif :

```powershell
python python\app.py
```

Les données de travail sont lues et écrites dans `agent/data/` (non suivi par
git). Ce dossier est créé au premier lancement et initialisé depuis
`apprentissage/datas/` s'il est vide.

- Le bouton **Sauvegarder** et la fermeture de la fenêtre écrivent
  `data/books.txt` et `data/users.txt`.
- Le bouton **Créer une sauvegarde** produit `books.txt.backup` et
  `users.txt.backup`. Si un `.backup` existe déjà, un message d'erreur est
  affiché dans la barre de statut au lieu de remplacer le fichier.

## Lancer les tests

Depuis `agent/`, avec le venv activé et le module compilé :

```sh
PYTHONPATH=build python -m unittest discover -s python/tests -v
```

Sous Windows (PowerShell) :

```powershell
$env:PYTHONPATH="build"; python -m unittest discover -s python\tests -v
```

Ces tests sont headless : ils n'ouvrent aucune fenêtre.

## Lancer l'ancien CLI

Le CLI reste disponible pour comparer avec la GUI. Depuis `agent/` :

```sh
./build/bibliotheque -d ../apprentissage/datas
```

L'option `0` du menu sauvegarde les données avant de quitter, comme la fermeture
de la fenêtre de la GUI.
