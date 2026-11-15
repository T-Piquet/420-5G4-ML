# Interface graphique de la bibliothèque

Application Python CustomTkinter inspirée de `layoutIdea.svg`. Elle reprend les
fonctions de l'application C++ `bibliotheque` et utilise les mêmes fichiers de
données pipe-delimités.

## Fonctions

- Tableau de bord avec statistiques et livres disponibles.
- Recherche par titre, auteur ou ISBN dans la section Livres.
- Ajout et suppression de livres.
- Ajout d'utilisateurs depuis toutes les sections avec le bouton `+ Usager`.
- Emprunt et retour de livres.
- Statistiques de disponibilité.
- Sauvegarde des données et création de fichiers `.backup`.
- Bascule soleil/lune entre les modes clair et sombre, mémorisée entre les lancements.
- Barre latérale repliable : icônes seules ou icônes et titres.

## Installation

Depuis la racine du dépôt :

```bash
python3 -m venv agent/gui/env
agent/gui/env/bin/python -m pip install -r agent/gui/.venv/requirements.txt
```

## Lancement

```bash
agent/gui/env/bin/python agent/gui/.venv/app.py
```

Par défaut, l'application utilise `agent/data/books.txt` et
`agent/data/users.txt`. Pour choisir un autre répertoire :

```bash
agent/gui/env/bin/python agent/gui/.venv/app.py --data-dir agent/data
```

## Mode d'affichage

Les icônes soleil et lune de la barre supérieure changent immédiatement le
thème de l'interface ; le soleil active le mode clair et la lune le mode
sombre. Le choix est enregistré dans
`~/.config/bibliotheque/settings.json` et restauré au prochain lancement.

L'interface nécessite un serveur X11 (`DISPLAY`). Dans le dev container, le
socket `/tmp/.X11-unix` et la variable `DISPLAY` sont déjà configurés.
