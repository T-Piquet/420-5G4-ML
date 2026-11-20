# Interface graphique (Python / customtkinter)

Interface de gestion de la bibliothèque personnelle, construite en MVC avec
customtkinter. La mise en page reprend `agent/maquetteUI.png` : barre latérale,
en-tête avec recherche, tableau des livres et actions en bas à droite.

Le coeur métier et la persistance sont assurés par le code C++ du projet,
exposé à Python avec **pybind11**. La couche Python assure la présentation, la
navigation, la validation des saisies et la recherche accent-insensible ;
l'état et les opérations de la bibliothèque restent en C++.

## Prérequis

- Python 3.13 avec Tkinter.
- Un compilateur C++17 et CMake (3.21 ou plus).
- Un serveur d'affichage X11 ou Wayland. Le devcontainer transmet déjà
  `DISPLAY` depuis l'hôte.

## Installation

```bash
cd agent/UI
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Le venv est dédié à l'interface et ignoré par Git. Il est distinct du venv
utilisé par les notebooks à la racine du dépôt.

## Compilation du module natif

Le module `bibliotheque_core` doit être compilé avant de lancer l'interface :

```bash
cd agent
./bindings/build.sh
```

Le script utilise le Python de `UI/.venv`, configure CMake avec pybind11 et
écrit le module dans `UI/app/`. Il est possible de faire la même chose à la
main :

```bash
cd agent
cmake -S . -B build-pybind11 \
    -DBUILD_PYTHON_BINDINGS=ON \
    -DPython_EXECUTABLE="$PWD/UI/.venv/bin/python" \
    -Dpybind11_DIR="$("$PWD/UI/.venv/bin/python" -m pybind11 --cmakedir)"
cmake --build build-pybind11 --target bibliotheque_core -j
```

Le module compilé est ignoré par Git. Après une modification du C++, relancer
`./bindings/build.sh`.

## Lancement

```bash
cd agent/UI
.venv/bin/python main.py
```

Si le module natif est absent, l'application s'arrête avec un message
indiquant la commande de compilation à exécuter.

## Données

L'application lit au démarrage les fichiers du dossier `agent/data/` avec le
`FileManager` C++ :

- `books.txt` : `titre|auteur|isbn|disponible|idEmprunteur` ;
- `users.txt` : `nom|identifiant|isbn1,isbn2`.

Les actions **Ajouter** un livre, **Emprunter**, **Retourner**, **Supprimer** et
**Ajouter un utilisateur** réécrivent les fichiers concernés au même format que
le programme C++. L'écriture se fait dans un fichier temporaire renommé ensuite,
afin de ne pas laisser un fichier tronqué en cas d'erreur. Pour revenir aux
données d'origine :

```bash
git checkout -- agent/data
```

## Fonctionnalités

- **Recherche** en direct par titre, auteur ou ISBN, insensible aux accents et
  à la casse.
- **Filtre « Disponibles uniquement »** pour n'afficher que les livres
  disponibles à prêter ; il se combine avec la recherche.
- **Tableau** des livres avec statut Disponible / Emprunté, sélection au clic
  et mise en évidence de la ligne.
- **Ajouter** un livre via une fenêtre modale (validation des champs et
  unicité de l'ISBN).
- **Emprunter** un livre disponible en choisissant l'utilisateur dans une
  liste ; le même bouton devient **Retourner** pour un livre emprunté.
- **Supprimer** le livre sélectionné après confirmation.
- **Section Utilisateurs** : liste alimentée par `users.txt` (nom, identifiant,
  nombre d'emprunts et titres empruntés), recherche accent-insensible par nom
  ou identifiant, et ajout d'un utilisateur via une fenêtre modale (unicité de
  l'identifiant).
- **Section Statistiques** : tableau de bord avec le total des livres, les
  livres disponibles, les livres empruntés, le nombre d'utilisateurs et le
  taux de disponibilité. Les compteurs proviennent du cœur C++
  (`getTotalBooks`, `getAvailableBookCount`, `getCheckedOutBookCount`).
- **Sauvegarde** : les actions enregistrent déjà automatiquement les fichiers ;
  le bouton « Sauvegarder données » de la sidebar force une écriture explicite
  via `FileManager::saveLibraryData` et affiche un retour visuel.
- **Créer une sauvegarde** : copie les fichiers actuels en `books.txt.backup`
  et `users.txt.backup` via `FileManager::createBackup`. Un clic suivant
  remplace la sauvegarde précédente ; le statut s'affiche sous les boutons.
- **Navigation** : Livres, Utilisateurs et Statistiques sont fonctionnels ;
  Emprunts affiche une section « à venir ».

## Tests

```bash
cd agent/UI
.venv/bin/python -m pytest -q
```

Les tests qui utilisent le modèle natif sont ignorés avec un message explicite
s'il n'a pas été compilé. Le test de fumée de la fenêtre nécessite un affichage
et est ignoré automatiquement s'il n'y en a pas :

```bash
xvfb-run -a .venv/bin/python -m pytest -q
```

## Structure MVC

```text
agent/
├── bindings/
│   ├── library_bindings.cpp             # module pybind11
│   └── build.sh                         # compilation du module
├── book.cpp/h, user.cpp/h
├── library.cpp/h, filemanager.cpp/h     # coeur C++ et persistance
└── UI/
    ├── main.py                          # composition root
    ├── app/
    │   ├── config.py                    # dimensions, palette, libellés
    │   ├── bibliotheque_core*.so        # module généré, ignoré
    │   ├── models/
    │   │   ├── book.py                  # dataclass Book
    │   │   ├── user.py                  # dataclass User
    │   │   └── library.py               # façade Python sur le C++
    │   ├── repositories/
    │   │   └── library_repository.py    # FileManager C++
    │   ├── views/
    │   │   ├── main_window.py           # fenêtre, sidebar, en-tête, pied
    │   │   ├── book_table.py            # tableau scrollable des livres
    │   │   ├── user_table.py            # tableau scrollable des utilisateurs
    │   │   ├── dialogs.py               # ajout livre/utilisateur, emprunt
    │   │   └── view_models.py           # BookRow / UserRow
    │   └── controllers/
    │       └── main_controller.py       # câblage vue ↔ modèle ↔ dépôt
    └── tests/
        ├── test_bindings.py
        ├── test_library.py
        ├── test_repository.py
        ├── test_controller.py
        └── test_view_smoke.py
```

Règles de dépendance :

- l'état des livres et des utilisateurs vit dans le C++ ; la façade Python ne
  fait que convertir et valider les entrées ;
- la vue n'importe pas le modèle ; elle reçoit des `BookRow` / `UserRow`
  prêts à afficher ;
- le contrôleur ne crée aucun widget ;
- le dépôt centralise les accès aux fichiers via le `FileManager` C++ ;
- seul `main.py` connaît les trois couches à la fois.
