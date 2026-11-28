# Gestion de bibliothèque — Atelier 3 : LLM agentique

## Présentation

Ce projet consiste à faire évoluer une application console de gestion de bibliothèque développée en C++ vers une application graphique Python utilisant CustomTkinter.

L'intégration entre Python et C++ est réalisée avec pybind11. La logique métier et la persistance des données demeurent en C++.

## Technologies utilisées

- C++17
- Python 3
- CMake
- pybind11
- CustomTkinter
- Docker et VS Code Dev Containers
- OpenCode
- Ollama — Qwen3 8B

## Structure du projet

| Fichier | Responsabilité |
|---|---|
| `book.cpp` / `book.h` | Gestion des livres |
| `user.cpp` / `user.h` | Gestion des utilisateurs |
| `library.cpp` / `library.h` | Logique métier |
| `filemanager.cpp` / `filemanager.h` | Persistance des données |
| `main.cpp` | Application console originale |
| `bindings.cpp` | Interface entre C++ et Python |
| `app.py` | Interface graphique |
| `test_bindings.py` | Tests d'interopérabilité |
| `CMakeLists.txt` | Configuration de la compilation |
| `AGENTS.md` | Directives de développement agentique |
| `chatsLogs/` | Historique des conversations avec OpenCode |
| `data/` | Fichiers de données |
| `.devcontainer/` | Configuration Docker |

## Installation

Ouvrir le dossier `agent` dans Visual Studio Code avec l'extension Dev Containers.

La configuration Docker prévoit l'installation des dépendances nécessaires à la compilation C++, à Python, à CustomTkinter et aux outils agentiques.

## Compilation

Depuis le dossier `agent` :

```bash
cmake -S . -B build
cmake --build build -j4
```

La compilation produit trois cibles :

- `bibliotheque_core` : bibliothèque statique contenant la logique métier.
- `bibliotheque` : application console.
- `bibliotheque_cpp` : module Python généré avec pybind11.

## Lancement de l'application console

```bash
./build/bibliotheque -d data
```

## Lancement de l'interface graphique

```bash
PYTHONPATH=build python app.py
```

Si un environnement virtuel local est utilisé, il doit être activé avant le lancement.

## Fonctionnalités

### Accueil

- Nombre total de livres.
- Nombre de livres disponibles.
- Nombre de livres empruntés.
- Nombre d'utilisateurs.

### Livres

- Affichage des livres.
- Ajout et suppression.
- Recherche par titre ou auteur.
- Filtrage des livres disponibles.

### Utilisateurs

- Affichage des utilisateurs.
- Ajout d'utilisateurs.
- Consultation des livres empruntés.

### Emprunts

- Emprunt d'un livre.
- Retour d'un livre.
- Consultation des emprunts en cours.

### Sauvegardes

- Enregistrement des données.
- Création de sauvegardes.
- Sauvegarde automatique à la fermeture.

## Tests

Pour exécuter les tests d'interopérabilité entre Python et C++ :

```bash
PYTHONPATH=build python test_bindings.py
```

Les tests couvrent l'ajout, la recherche, l'emprunt, le retour, la suppression ainsi que la sauvegarde et le chargement des données.

## Configuration Windows avec WSLg

Sous Windows avec WSL2 et WSLg, le socket X11 peut être accessible à l'emplacement suivant :

```text
/mnt/wslg/.X11-unix
```

Dans ce cas, adapter le montage dans `devcontainer.json` :

```json
"mounts": [
    "source=/mnt/wslg/.X11-unix,target=/tmp/.X11-unix,type=bind"
],
"containerEnv": {
    "DISPLAY": ":0"
}
```

Pour vérifier le fonctionnement de l'affichage graphique :

```bash
python -m tkinter
```

## Développement agentique

OpenCode a été utilisé avec le modèle Qwen3 8B exécuté localement par Ollama.

Le développement comprend :

- L'analyse du projet C++ existant.
- La planification de l'architecture.
- La conception des maquettes.
- La rédaction des directives AGENTS.md.
- La génération et la révision du code.
- La validation de l'intégration Python/C++.

Certaines générations produites par l'agent ont nécessité des corrections et des interventions externes, notamment pour la configuration CMake, les bindings et l'interface graphique.

Les conversations avec OpenCode sont conservées dans le dossier `chatsLogs/`.

### Configuration d'Ollama

Le fichier `opencode.json` utilise une instance Ollama exécutée sur la machine hôte, accessible depuis Docker à l'adresse :

```text
http://host.docker.internal:11434/v1
```

Pour reproduire le modèle utilisé :

```bash
ollama pull qwen3:8b
```

Créer un fichier `Modelfile` contenant :

```text
FROM qwen3:8b
PARAMETER num_ctx 12288
PARAMETER temperature 0.2
```

Puis exécuter :

```bash
ollama create qwen3-agent -f Modelfile
```

Lancer OpenCode depuis le dossier `agent` :

```bash
opencode
```

L'adresse du serveur Ollama peut être adaptée selon l'environnement utilisé.

## Persistance

Les données sont conservées dans les fichiers `data/books.txt` et `data/users.txt`.

L'application console et l'application graphique utilisent la même logique métier C++ et le même mécanisme de persistance.