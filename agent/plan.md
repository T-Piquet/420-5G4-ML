# Plan — Partie 3 : Interface customTkinter + pybind11

Plan élaboré avec Claude (claude.ai), avec l'accord de l'enseignant.

## Décisions de conception
- La GUI n'utilise PAS les méthodes `display...()` (elles affichent avec `cout`).
  Elle utilise les méthodes qui retournent des données (`getAllBooks()`, getters de `Book`/`User`).
- Le tri (option 14) se fait en Python sur la liste retournée par `getAllBooks()`.
- La journalisation : la GUI appelle `ActivityLogger` après chaque action
  (comme le faisait `main.cpp`), pour ne pas modifier la logique C++.
- Le code de liaison pybind11 va dans `python/` pour ne pas casser le build CMake
  (`file(GLOB "*.cpp")` prendrait tous les .cpp de la racine).

## Étapes (une étape = un commit)

### A. Liaison C++ ↔ Python (pybind11)
- [x] A1. Exposer `Book` (constructeurs + getters) — test : créer un Book en Python et afficher son titre
- [x] A2. Exposer `User` (constructeur + getters) — test : créer un User en Python et afficher son nom
- [x] A3. Exposer `Library` (ajout, recherche, emprunt, retour, statistiques) — test : ajouter un livre et le retrouver par ISBN
- [x] A4. Exposer `FileManager` — test : charger `data/` et afficher le nombre de livres
- [x] A5. Exposer `ActivityLogger` — test : écrire une ligne dans `journal.log`

### B. Interface customTkinter
- [x] B1. Fenêtre principale vide avec des onglets (Livres, Utilisateurs, Emprunts, Statistiques)
- [x] B2. Onglet Livres : tableau de tous les livres (titre, auteur, ISBN, disponible)
- [x] B3. Onglet Livres : recherche par titre / auteur + filtre « disponibles seulement » + tri
- [ ] B4. Onglet Livres : ajouter / supprimer un livre
- [ ] B5. Onglet Utilisateurs : liste + ajouter un utilisateur
- [ ] B6. Onglet Emprunts : emprunter / retourner un livre
- [ ] B7. Onglet Statistiques : total, disponibles, empruntés, utilisateurs
- [ ] B8. Boutons Sauvegarder / Créer une sauvegarde / Quitter (sauvegarde avant de quitter)
- [ ] B9. Journalisation de chaque action via `ActivityLogger`

### C. Finition
- [ ] C1. Messages d'erreur clairs (ISBN déjà existant, livre introuvable, livre déjà emprunté…)
- [ ] C2. Mettre à jour `AGENTS.md` et `README.md` (comment lancer la GUI)