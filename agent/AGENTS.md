# AGENTS.md

## Projet : Gestion de Bibliothèque Personnelle

### 1. Architecture C++
- **Fichiers conservés** : `main.cpp`, `library.h`, `library.cpp`, `book.h`, `book.cpp`, `user.h`, `user.cpp`, `filemanager.h`, `filemanager.cpp`
- **Instance unique** : Utiliser une seule instance de `Library` dans l'application (sans implémentation du patron Singleton)
- **Fichiers de données** : `data/books.txt`, `data/users.txt` (format non spécifié, à valider)
- **Contraintes** : Ne pas modifier le comportement des fichiers C++ existants

### 2. Intégration Python
- **Module Python** : `bibliotheque_cpp` (nom du module)
- **Fichiers bindings** : `bindings.cpp` (implémentation pybind11)
- **CMake** : Cible `bibliotheque` existante conservée
- **Interopérabilité** : Bibliothèque C++ commune au programme console et au module Python

### 3. Interface Graphique
- **Composants** : Utiliser CustomTkinter pour les cinq écrans
- **Navigation** : Sidebar verticale gauche avec les cinq écrans (Accueil, Livres, Utilisateurs, Emprunts, Sauvegardes)
- **Contenu** : Zone de droite adaptative selon l'écran sélectionné
- **Bouton Quitter** : Sauvegarde automatique avant fermeture

### 4. Plan de Développement
1. **Configuration CMake**
   - Valider la configuration existante pour le programme console et le module Python
   - Ajouter les dépendances nécessaires pour pybind11

2. **Bindings pybind11**
   - Créer `bindings.cpp` pour exposer les classes C++ à Python
   - Vérifier les signatures des méthodes dans les fichiers `.h` avant toute implémentation

3. **Tests des bindings**
   - Valider l'interopérabilité entre C++ et Python
   - Tester les méthodes exposées depuis Python

4. **Interface graphique CustomTkinter**
   - Implémenter la sidebar verticale avec les cinq écrans
   - Créer les composants graphiques pour chaque écran (cartes, tableaux, formulaires)

5. **Intégration des fonctionnalités**
   - Associer les écrans à la logique métier existante
   - Garantir la cohérence entre l'interface et les méthodes C++

6. **Tests fonctionnels et documentation**
   - Valider chaque écran et ses interactions
   - Mettre à jour le `README.md` avec les instructions d'utilisation et de compilation
   - Ajouter des commentaires en français dans les fichiers C++ et Python

### 5. Contraintes
- **Pas de restauration** : Ne prévoir aucune fonctionnalité de restauration des données
- **Fichiers de données** : Utiliser des données temporaires pour les tests (protéger les fichiers originaux)
- **Sécurité** : Ne pas modifier le comportement des fichiers C++ existants
- **Documentation** : Tous les commentaires doivent être en français

### 6. Gestion des Commits
- **Commits réguliers** : Effectuer un commit après validation de chaque étape
- **Messages clairs** : Utiliser des messages de commit descriptifs pour chaque phase de développement

### 7. Mise à jour du README.md
- **Instructions** : Ajouter les étapes de compilation, d'installation et d'utilisation
- **Compatibilité** : Garantir la compatibilité entre le programme console, le module Python et l'interface graphique

### 8. Validation finale
- **Tests complets** : Valider toutes les fonctionnalités avec les cinq écrans
- **Documentation** : Assurer une documentation claire et complète en français pour les utilisateurs finaux