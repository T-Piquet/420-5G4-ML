# Interface graphique (customtkinter)

Fenêtre minimale de l'application de gestion de bibliothèque.

## Installation

```bash
cd agent/ui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
cd agent/ui
source .venv/bin/activate
python app.py
```

## Affichage (X11)

Le devcontainer monte le socket X11 et transmet `DISPLAY`. Si la fenêtre ne
s'affiche pas (`couldn't connect to display`), vérifier que `DISPLAY` est défini
et que le serveur X de l'hôte autorise la connexion (`xhost +local:`).
