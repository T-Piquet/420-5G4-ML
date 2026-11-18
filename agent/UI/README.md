# Interface graphique (Python / customtkinter)

Interface de démonstration en MVC pour l'atelier. La fenêtre initiale affiche
un message et un compteur afin de valider le cycle
**vue → contrôleur → modèle → vue**.

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

## Tests

```bash
cd agent/UI
.venv/bin/python -m pytest -q
```

Le test de fumée de la fenêtre nécessite un affichage et est ignoré
automatiquement s'il n'y en a pas. Sur une machine sans écran :

```bash
xvfb-run -a .venv/bin/python -m pytest -q
```

## Structure MVC

```text
UI/
├── main.py                      # composition root : assemble les couches
├── app/
│   ├── config.py                # constantes de l'interface
│   ├── models/app_model.py      # état et logique, sans Tkinter
│   ├── views/main_window.py     # fenêtre et widgets customtkinter
│   └── controllers/main_controller.py  # câblage vue ↔ modèle
└── tests/
    ├── test_model.py
    ├── test_controller.py       # vue factice, sans Tkinter
    └── test_view_smoke.py       # instanciation réelle de la fenêtre
```

Règles de dépendance :

- le modèle n'importe jamais Tkinter ;
- la vue ne contient pas de logique métier et n'importe pas le modèle ;
- le contrôleur ne crée aucun widget ;
- seul `main.py` connaît les trois couches à la fois.
