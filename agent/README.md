Remise de Toni Eliamokhtar

# Bibliothèque personnelle — C++ et interface graphique Python

Le projet contient le programme console C++ `bibliotheque` et, depuis la
partie 4, une interface graphique Python (customtkinter) qui utilise les mêmes
classes C++ via pybind11.

## Compiler le projet

Vous pouvez utiliser le dev container C++ de VS Code. Le projet utilise CMake
et nécessite C++17, `pybind11-dev`, `python3-dev`, `python3-venv` et
`python3-tk` (déjà présents dans le dev container).

Depuis la racine du dépôt :

```bash
python3 -m venv agent/.venv
source agent/.venv/bin/activate
pip install -r agent/requirements.txt

cmake -S agent -B agent/build
cmake --build agent/build -j
```

Pour compiler uniquement le programme console, sans les bindings Python :

```bash
cmake -S agent -B agent/build -DBUILD_PYTHON_BINDINGS=OFF
cmake --build agent/build -j
```

Le module Python est produit dans `agent/build/python/`.

## Programme console

```bash
./agent/build/bibliotheque --data-dir agent/data
```

Le programme console reste fonctionnel et sauvegarde les données à la sortie.
Pour tester sans modifier les fichiers suivis par Git, utilisez une copie :

```bash
rm -rf /tmp/biblio-data
cp -r agent/data /tmp/biblio-data
./agent/build/bibliotheque -d /tmp/biblio-data
```

## Interface graphique

```bash
source agent/.venv/bin/activate
PYTHONPATH=agent/build/python python agent/gui/app.py --data-dir agent/data
```

`--data-dir` (ou `-d`) est optionnel : par défaut, l'application utilise
`agent/data`.

Pour un essai manuel sans risque :

```bash
rm -rf /tmp/biblio-data
cp -r agent/data /tmp/biblio-data
source agent/.venv/bin/activate
PYTHONPATH=agent/build/python python agent/gui/app.py --data-dir /tmp/biblio-data
```

Les modifications ne sont écrites dans `books.txt` et `users.txt` que lors
d'un clic sur « Sauvegarder les données » ou après confirmation à la fermeture.
« Créer une sauvegarde » produit `books.txt.backup` et `users.txt.backup`.

### Affichage graphique sous WSL / Linux

Le dev container monte le socket X11 (`/tmp/.X11-unix`), transmet `DISPLAY` et
utilise `--net=host`. Sous WSL2 avec WSLg, l'affichage fonctionne directement.

Vérification rapide :

```bash
echo "$DISPLAY"
ls -la /tmp/.X11-unix
python -c "import tkinter; r=tkinter.Tk(); print('GUI OK'); r.destroy()"
```

Si `DISPLAY` est vide, utilisez `export DISPLAY=:0` (WSLg) ou l'adresse du
serveur X de l'hôte. Avec un serveur X externe, autorisez l'accès avec `xhost`.

## Tests

```bash
source agent/.venv/bin/activate
PYTHONPATH=agent/build/python pytest -q agent/tests
```

Les tests utilisent des copies temporaires de `agent/data`. Une garde vérifie
que les vrais fichiers `books.txt` et `users.txt` ne sont pas modifiés.

Le test graphique nécessite un serveur X11 (`DISPLAY`). Sans affichage, il est
ignoré automatiquement. La vérification visuelle de la fenêtre reste à faire
manuellement.

## Répertoire data

`agent/data/` contient `books.txt` et `users.txt` pour les essais, ainsi que
les jeux de données des parties 1 à 3.

Le format des fichiers est le suivant :

- `books.txt` : `titre|auteur|isbn|disponible(1/0)|idEmprunteur`
- `users.txt` : `nom|idUtilisateur|isbn1,isbn2,...`

## Journal des échanges IA

Les échanges de la partie 4 sont exportés dans `chatsLogs/` à la racine du
dépôt.
