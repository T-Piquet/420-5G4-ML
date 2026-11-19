# Interface graphique (Python / customtkinter)

Interface de gestion de la bibliothèque personnelle, construite en MVC avec
customtkinter. La mise en page reprend `agent/maquetteUI.png` : barre latérale,
en-tête avec recherche, tableau des livres et actions en bas à droite.

## Prérequis

- Python 3.13 avec Tkinter.
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

## Lancement

```bash
cd agent/UI
.venv/bin/python main.py
```

## Données

L'application lit au démarrage les fichiers du dossier `agent/data/` :

- `books.txt` : `titre|auteur|isbn|disponible|idEmprunteur` ;
- `users.txt` : `nom|identifiant|isbn1,isbn2`.

Les actions **Ajouter**, **Emprunter**, **Retourner** et **Supprimer**
réécrivent ces deux fichiers au même format que le programme C++. Pour revenir
aux données d'origine :

```bash
git checkout -- agent/data
```

## Fonctionnalités

- **Recherche** en direct par titre, auteur ou ISBN, insensible aux accents et
  à la casse.
- **Tableau** des livres avec statut Disponible / Emprunté, sélection au clic
  et mise en évidence de la ligne.
- **Ajouter** un livre via une fenêtre modale (validation des champs et
  unicité de l'ISBN).
- **Emprunter** un livre disponible en choisissant l'utilisateur dans une
  liste ; le même bouton devient **Retourner** pour un livre emprunté.
- **Supprimer** le livre sélectionné après confirmation.
- **Navigation** : Livres est fonctionnel ; Utilisateurs, Emprunts et
  Statistiques affichent une section « à venir ».

## Tests

```bash
cd agent/UI
.venv/bin/python -m pytest -q
```

Le test de fumée de la fenêtre nécessite un affichage et est ignoré
automatiquement s'il n'y en a pas :

```bash
xvfb-run -a .venv/bin/python -m pytest -q
```

## Structure MVC

```text
UI/
├── main.py                              # composition root
├── app/
│   ├── config.py                        # dimensions, palette, libellés
│   ├── models/
│   │   ├── book.py                      # Book
│   │   ├── user.py                      # User
│   │   └── library.py                   # règles métier et recherche
│   ├── repositories/
│   │   └── library_repository.py        # lecture/écriture de agent/data
│   ├── views/
│   │   ├── main_window.py               # fenêtre, sidebar, en-tête, pied
│   │   ├── book_table.py                # tableau scrollable
│   │   ├── dialogs.py                   # ajout et choix d'utilisateur
│   │   └── view_models.py               # BookRow / UserRow
│   └── controllers/
│       └── main_controller.py           # câblage vue ↔ modèle ↔ dépôt
└── tests/
    ├── test_library.py
    ├── test_repository.py
    ├── test_controller.py
    └── test_view_smoke.py
```

Règles de dépendance :

- le modèle n'importe jamais Tkinter ;
- la vue n'importe pas le modèle ; elle reçoit des `BookRow` / `UserRow`
  prêts à afficher ;
- le contrôleur ne crée aucun widget ;
- le dépôt centralise les accès aux fichiers ;
- seul `main.py` connaît les trois couches à la fois.
