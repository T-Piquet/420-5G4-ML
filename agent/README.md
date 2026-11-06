# Bibliothèque personnelle — C++17, pybind11 et CustomTkinter

Application de gestion de bibliothèque personnelle réalisée dans le cadre du cours
**420-5G4 — Atelier ML** (partie 3).

Le projet réunit :

- un **cœur métier en C++17** (`Book`, `User`, `Library`, `FileManager`) ;
- une **interface Python** exposée avec **pybind11** (module `bibliotheque_cpp`) ;
- une **interface graphique moderne en CustomTkinter**, entièrement en français ;
- une **sauvegarde automatique** des données après chaque modification.

Le devcontainer fourni installe tout le nécessaire (CMake, compilateur C++,
pybind11, Tkinter, CustomTkinter) et expose un bureau graphique via **noVNC**
sur le port **6080**.

---

## 1. Démarrage rapide

### Prérequis

- **Docker** démarré (Docker Desktop sous Windows/macOS, Docker Engine sous Linux) ;
- **VS Code** avec l'extension **Dev Containers** ;
- Git (pour récupérer le dépôt).

Aucune installation de CMake, Python, Tkinter ou CustomTkinter n'est nécessaire
sur la machine : tout se passe dans le conteneur.

### Étape 1 — Ouvrir le dossier `agent/` dans VS Code

Le fichier de configuration du devcontainer se trouve dans `agent/.devcontainer`.
Il faut donc ouvrir **le dossier `agent/`**, et non la racine du dépôt :

```bash
code /chemin/vers/le-depot/agent
```

> Le dossier `agent/` doit être la racine du projet ouverte dans VS Code :
> c'est lui qui contient `.devcontainer/`. Si VS Code est déjà ouvert sur la
> racine du dépôt, utilisez **Fichier → Ouvrir le dossier…** puis sélectionnez
> `agent/`.

### Étape 2 — Démarrer le conteneur

Dans VS Code :

1. `Ctrl+Shift+P` (ou `Cmd+Shift+P` sous macOS) ;
2. exécutez **Dev Containers: Reopen in Container**.

La première construction prend quelques minutes (téléchargement de l'image et
installation des dépendances). Les fois suivantes, le conteneur démarre en
quelques secondes.

### Étape 3 — Compiler le projet

Ouvrez un terminal intégré (**Terminal → Nouveau terminal**). Le terminal
s'exécute déjà **dans le conteneur**, dans le dossier du projet :

```bash
cmake -S . -B build -DPython_EXECUTABLE=$(which python3)
cmake --build build
```

Cette commande compile :

- l'exécutable console `build/bibliotheque` ;
- le module Python `build/bibliotheque_cpp*.so`.

> Le module Python est compilé pour l'interpréteur `python3` du conteneur.
> C'est le même interpréteur qui lance l'interface graphique : il n'y a donc
> aucun problème de version.

### Étape 4 — Vérifier que tout fonctionne

```bash
PYTHONPATH=build python3 tests/test_bindings.py
PYTHONPATH=build python3 tests/test_service.py
```

Résultat attendu :

```text
8 tests reussis.
7 tests reussis.
```

Les tests utilisent uniquement des dossiers temporaires : ils ne modifient
jamais `data/`.

### Étape 5 — Lancer l'interface graphique

```bash
PYTHONPATH=build python3 gui/app.py --data-dir data
```

Puis :

1. VS Code ouvre normalement automatiquement le port **6080** dans le
   navigateur. Sinon, allez dans l'onglet **Ports** et ouvrez le port `6080`
   (libellé *CustomTkinter GUI Desktop (noVNC)*).
2. Dans le navigateur : **http://localhost:6080**
3. Mot de passe du bureau : **`vscode`**

La fenêtre **« Bibliothèque personnelle »** apparaît dans le bureau noVNC.

> Si la fenêtre ne s'affiche pas, vérifiez que la variable `DISPLAY` vaut
> `:1` dans le terminal :
>
> ```bash
> echo $DISPLAY
> ```
>
> Sinon, lancez `export DISPLAY=:1` puis relancez l'application.

### Étape 6 (facultative) — Lancer la version console

L'exécutable C++ d'origine reste disponible :

```bash
./build/bibliotheque -d data
```

Il propose un menu interactif (affichage, ajout, emprunt, retour, sauvegarde).

---

## 2. Utilisation de l'interface

L'interface comporte une barre latérale de navigation et quatre vues :

| Vue | Contenu |
| --- | --- |
| **Tableau de bord** | Nombre total de livres, livres disponibles, emprunts en cours, nombre d'adhérents, bouton de sauvegarde |
| **Catalogue** | Recherche par titre/auteur, filtre Tous / Disponibles / Empruntés, ajout et suppression de livres |
| **Adhérents** | Nom, identifiant, nombre et liste des livres empruntés, ajout d'adhérents |
| **Emprunts en cours** | Livres empruntés avec l'identité de l'emprunteur, nouvel emprunt et retour |

### Actions disponibles

- **Ajouter un livre** : titre, auteur et ISBN. Un ISBN déjà présent est refusé
  avec un message explicite.
- **Supprimer un livre** : sélectionnez d'abord une ligne dans le catalogue,
  puis cliquez sur **Supprimer le livre sélectionné**. Une confirmation est
  demandée. La suppression d'un livre **en cours d'emprunt** est bloquée.
- **Ajouter un adhérent** : nom et identifiant. Un identifiant déjà utilisé est
  refusé.
- **Emprunter un livre** : choisissez un livre disponible et un adhérent dans
  les listes déroulantes (la saisie directe de l'ISBN ou de l'identifiant est
  aussi acceptée).
- **Retourner un livre** : sélectionnez un emprunt dans la vue *Emprunts en
  cours*, puis cliquez sur **Retourner le livre sélectionné**.
- **Créer une sauvegarde** : copie `books.txt` et `users.txt` en
  `books.txt.backup` et `users.txt.backup`. Si une sauvegarde existe déjà,
  l'opération est refusée avec un message explicite.

Chaque action réussie est **enregistrée immédiatement sur le disque** et
confirmée par une bannière verte. Les erreurs sont affichées en français dans
la boîte de dialogue ou la bannière.

### Thème et actualisation

- Le commutateur **Mode sombre** de la barre latérale bascule entre thème clair
  et thème sombre.
- Le bouton **Actualiser** relit les fichiers du dossier de données.

---

## 3. Structure du projet

```text
agent/
├── .devcontainer/          # Environnement VS Code (C++, Python, Tkinter, noVNC)
├── book.h / book.cpp       # Livre
├── user.h / user.cpp       # Adhérent
├── library.h / library.cpp # Bibliothèque (livres, adhérents, emprunts)
├── filemanager.h / .cpp    # Lecture/écriture des fichiers et sauvegardes
├── main.cpp                # Application console
├── bindings.cpp            # Module Python « bibliotheque_cpp » (pybind11)
├── CMakeLists.txt          # Compilation du CLI et du module Python
├── gui/
│   ├── app.py              # Point d'entrée CustomTkinter, navigation, thème
│   ├── service.py          # Couche de service : lectures, mutations, auto-save
│   ├── components/
│   │   ├── banner.py       # Bannière de succès / erreur
│   │   ├── dialogs.py      # Formulaires, confirmations, messages
│   │   ├── kpi_card.py     # Carte de statistique
│   │   ├── status_bar.py   # Barre d'état
│   │   └── table.py        # Tableau défilant avec sélection
│   └── views/
│       ├── dashboard_view.py
│       ├── catalogue_view.py
│       ├── users_view.py
│       └── loans_view.py
├── tests/
│   ├── test_bindings.py    # Tests du module C++ et de la persistance
│   └── test_service.py     # Tests des mutations et de l'auto-sauvegarde
├── data/
│   ├── books.txt           # Jeu de données d'exemple
│   └── users.txt
└── build/                  # Généré par CMake (ignoré par Git)
```

---

## 4. Format des données

Les fichiers sont au format texte UTF-8, un enregistrement par ligne.

**`data/books.txt`**

```text
titre|auteur|isbn|disponible|idEmprunteur
```

- `disponible` : `1` si le livre est disponible, `0` s'il est emprunté ;
- `idEmprunteur` : vide si le livre est disponible.

Exemple :

```text
Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|
Les Misérables|Victor Hugo|9782253096337|0|USR001
```

**`data/users.txt`**

```text
nom|identifiant|isbn1,isbn2,...
```

Exemple :

```text
Marie Dubois|USR001|9782253096337
Jean Martin|USR002|
```

Le jeu de données fourni contient **41 livres**, **25 adhérents** et
**14 emprunts**.

### Utiliser un autre dossier de données

```bash
PYTHONPATH=build python3 gui/app.py --data-dir /chemin/vers/mes/donnees
```

Le dossier est créé automatiquement s'il n'existe pas. Sans `--data-dir`,
l'application utilise `agent/data`.

### Réinitialiser les données d'exemple

L'interface enregistre les modifications directement dans `data/`. Pour
revenir au jeu de données du dépôt :

```bash
git restore data/books.txt data/users.txt
rm -f data/books.txt.backup data/users.txt.backup
```

---

## 5. Tests

```bash
PYTHONPATH=build python3 tests/test_bindings.py
PYTHONPATH=build python3 tests/test_service.py
```

- **`test_bindings.py`** (8 tests) : constructeurs, recherche, emprunts,
  aller-retour de persistance, sauvegarde, protection du dossier `data/`.
- **`test_service.py`** (7 tests) : validations, doublons, suppression d'un
  livre emprunté, emprunt/retour, auto-sauvegarde, sauvegardes, protection du
  dossier `data/`.

Les deux scripts sont autonomes (pas de `pytest`) et affichent `OK` par test,
puis le nombre total de tests réussis.

---

## 6. Dépannage

| Problème | Solution |
| --- | --- |
| `ModuleNotFoundError: No module named 'bibliotheque_cpp'` | Compiler avec `cmake --build build`, puis lancer avec `PYTHONPATH=build`. |
| `Could not find a package configuration file provided by "pybind11"` | Reconfigurer avec `cmake -S . -B build -DPython_EXECUTABLE=$(which python3) -Dpybind11_DIR=$(python3 -m pybind11 --cmakedir)`. |
| `ModuleNotFoundError: No module named 'customtkinter'` | `pip3 install --break-system-packages customtkinter packaging`, puis relancer. |
| Le module Python ne s'importe plus après un changement d'environnement (hôte ↔ conteneur) | Supprimer le dossier `build/` puis recompiler dans le conteneur : `rm -rf build && cmake -S . -B build -DPython_EXECUTABLE=$(which python3) && cmake --build build`. |
| La page noVNC ne s'ouvre pas | Vérifier que le port `6080` est bien transféré (onglet **Ports**), puis ouvrir `http://localhost:6080`. |
| `couldn't connect to display` | Vérifier `echo $DISPLAY` (attendu : `:1`), sinon `export DISPLAY=:1`. |
| « Une sauvegarde existe déjà » | Supprimer `data/books.txt.backup` et `data/users.txt.backup`, puis relancer la sauvegarde. |
| Le GUI ne reflète pas une modification du code C++ | Recompiler (`cmake --build build`) et relancer l'application. |

---

## 7. Fonctionnalités par jalon

| Jalon | Contenu |
| --- | --- |
| **J1** | Module `bibliotheque_cpp` exposé à Python avec pybind11 ; compilation CMake du CLI et du module. |
| **J2** | Tests autonomes des bindings et de la persistance (`tests/test_bindings.py`). |
| **J3** | Interface CustomTkinter en lecture seule : navigation, tableau de bord, catalogue, adhérents, emprunts. |
| **J4** | Mutations complètes, validation en français, auto-sauvegarde, confirmations, bannières et sauvegardes `.backup`. |

---

## 8. Remarques techniques

- Les collections renvoyées par `Library` sont des **copies** : l'interface
  travaille sur des instantanés Python et ne conserve jamais de pointeur C++
  après une suppression.
- La recherche est effectuée en Python (`casefold`) pour gérer correctement les
  accents français.
- Le format de fichier utilise `|` comme séparateur : les champs contenant ce
  caractère (ou un retour à la ligne) sont refusés par le service.
- `build/`, `__pycache__/` et les fichiers `.backup` ne sont pas suivis par Git.
