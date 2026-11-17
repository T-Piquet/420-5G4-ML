# Atelier ML

## Première partie

Dans le répertoire `agent/apprentissage/`.

## Deuxième partie

Dans le répertoire `agent/analyse_image/`.

## Troisième et quatrième parties

Le répertoire `agent/` contient le code C++ du projet (gestion de bibliothèque
personnelle) et le devcontainer pour la redirection du serveur graphique.

- `agent/` : programme console `bibliotheque`, construit avec CMake.
- `agent/bindings/` : bindings pybind11 exposant les classes C++ à Python.
- `agent/gui/` : interface graphique Python avec customtkinter.
- `agent/tests/` : tests des bindings, de la GUI et du CLI.

Voir `agent/README.md` pour les commandes de compilation, de lancement et de test.
