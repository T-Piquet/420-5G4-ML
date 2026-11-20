# AGENTS.md

## Projet

Gestion de bibliothèque en C++17 (code du TP C++). Menu en ligne de commande dans `main.cpp` (13 options : livres, utilisateurs, emprunt, retour, statistiques, sauvegarde).

## Classes

- `Book` (book.h/.cpp) : titre, auteur, ISBN, disponibilité, emprunteur
- `User` (user.h/.cpp) : nom, ID, livres empruntés
- `Library` (library.h/.cpp) : addBook, removeBook, findBookByISBN, searchBooksByTitle, getAllBooks, addUser, getAllUsers, checkOutBook, returnBook, statistiques
- `FileManager` (filemanager.h/.cpp) : loadLibraryData, saveLibraryData (fichiers texte dans `data/`)

## Compiler et lancer

    mkdir build && cd build && cmake .. && make
    ./bibliotheque -d ../data

## Objectif de l'atelier

Remplacer le menu en ligne de commande par une interface graphique customtkinter (Python), reliée au code C++ avec pybind11.

## État actuel

Module pybind11 `bibliotheque_py` fait et testé (import Python OK).

GUI customtkinter `gui.py` faite (liste des livres, ajouter, emprunter, retourner, sauvegarder), reliée au C++ par `bibliotheque_py`.
