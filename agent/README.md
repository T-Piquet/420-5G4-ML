# Construire le projet
Vous pouvez utiliser un dev container de base C++ de VScode.
Le projet utilise cmake, pensez à l'inclure dans votre dev container.

Voici les lignes de commandes pour compiler le projet:
```
$ mkdir build
$ cd build
$ cmake ..
$ make
```

# Répertoire data

Il contient 2 fichiers `books.txt`et `users.txt` que vous pouvez utilisez pour tester votre code.
Pour ca il suffit de donner chemin vers le repertoire data avec l'application `bibliotheque -d <chemin verrs data>`

# Rendu du TP

**Auteur : Sean Nguyen**

## Fonctionnalités implémentées

- **Complétion du code manquant** : écriture de `book.cpp` à partir de `book.h`. Le format de fichier est `titre|auteur|isbn|disponibilité|idEmprunteur`

- **Interface et expérience utilisateur : numérotation automatique des ID utilisateurs.** Le menu 7 ne demande plus l'ID : `Library::generateUserId()` prend le plus grand numéro `USRnnn` existant et ajoute 1.

- **Gestion des données : tri des résultats par titre ou auteur** avec `std::sort` (menu 14), insensible à la casse. Limite connue : `::tolower` ne gère pas les accents UTF-8, donc « Émile Zola » est classé après « Voltaire ».

- **Journal d'activités** : classe `ActivityLogger`, fichier `journal.log` ouvert en ajout (`std::ios::app`) donc conservé entre les sessions et créé au besoin. Il est placé dans le répertoire `--data-dir`, ou dans le répertoire courant sans cette option. Actions consignées : ajout/suppression de livre, emprunt, retour, ajout d'utilisateur.

- **Correction du bug** : sans `--data-dir` n'essaient plus d'écrire dans un chemin vide, et affichent un message explicite.

## Question 1: 

Une fonctionnalité que nous avons peu vue en cours est l'utilisation des lambdas avec les algorithmes de la STL en C++.

Dans la méthode Library::displaySortedBooks, on utilise std::sort pour trier les livres par titre ou par auteur. On lui passe une lambda, qui est une fonction anonyme servant à comparer deux livres et à déterminer lequel vient en premier. 
``` c++ 
    sort(sorted.begin(), sorted.end(), [byTitle](const Book* a, const Book* b) {
    if (byTitle) {
        return toLower(a->getTitle()) < toLower(b->getTitle());
    }
    return toLower(a->getAuthor()) < toLower(b->getAuthor());
});
```
Les crochets [byTitle] permettent à la lambda d'utiliser une copie de la variable byTitle pour savoir si le tri doit se faire par titre ou par auteur. Les paramètres a et b représentent deux livres à comparer.

Si byTitle est vrai, la lambda compare les titres. Sinon, elle compare les auteurs. La fonction toLower permet de convertir les textes en minuscules pour que le tri ne dépende pas des majuscules et des minuscules.

std::sort utilise cette comparaison pour trier les livres dans l'ordre alphabétique. Avant cela, on copie les pointeurs des livres dans un nouveau vecteur sorted, afin de trier cette copie sans modifier l'ordre de la liste originale.

## Question 2 : Options de développement possibles

Pour gérer des millions de livres, je remplacerais les fichiers texte par une base de données comme PostgreSQL. Avec des millions de livres, lire tous les fichiers au démarrage et rechercher les livres un par un serait trop lent. Une base de données permettrait de retrouver les livres plus rapidement grâce aux index et de gérer les emprunts de façon plus sécuritaire.

Pour connecter le programme C++ à la base de données, j'utiliserais **ODBC** au lieu de libpqxx. ODBC permet au programme d'envoyer des requêtes SQL et de récupérer les résultats. Je remplacerais aussi la classe `FileManager` par une classe `Database` qui s'occuperait de gérer les données.

Si la bibliothèque devient encore plus grande et que plusieurs personnes doivent utiliser le système en même temps, je pourrais créer une API REST pour permettre à différentes applications d'accéder aux mêmes données. Cela rendrait le système plus facile à faire évoluer.

# Partie 3 : Interface graphique (customTkinter + pybind11)

Le menu en ligne de commande est remplacé par une interface graphique Python
(customTkinter) qui appelle directement la logique C++ du TP grâce à pybind11.
La logique C++ (`book`, `user`, `library`, `filemanager`, `activitylogger`) n'a pas été modifiée.

## Lancer l'application
Dans le devcontainer (dossier `agent/`) :

1. Compiler le module Python `biblio` :
   ```
   g++ -O2 -shared -std=c++17 -fPIC $(python3 -m pybind11 --includes) python/bindings.cpp book.cpp user.cpp library.cpp filemanager.cpp activitylogger.cpp -o python/biblio$(python3-config --extension-suffix)
   ```
2. Lancer l'interface :
   ```
   cd python && python3 app.py
   ```
3. La fenêtre s'affiche dans le bureau virtuel : http://localhost:6080 (mot de passe `vscode`).

Test sans interface : `cd python && python3 test_biblio.py`.

## Fonctionnalités
| Onglet / bouton | Menu d'origine | Fonction |
|---|---|---|
| Livres | 1 à 6, 14 | tableau des livres, recherche par titre/auteur, filtre « disponibles seulement », tri, ajout, suppression |
| Utilisateurs | 7, 8 | liste des utilisateurs, ajout avec ID généré automatiquement |
| Emprunts | 9, 10 | emprunter un livre disponible, retourner un livre emprunté |
| Statistiques | 11 | total, disponibles, empruntés, nombre d'utilisateurs (mis à jour après chaque action) |
| Sauvegarder / Créer une sauvegarde / Quitter | 12, 13, 0 | sauvegarde des fichiers, copie `.backup`, sauvegarde avant de quitter (aussi avec le X) |

Chaque action est consignée dans `data/journal.log` avec `ActivityLogger`.

## Décisions de conception
- La GUI n'utilise pas les méthodes `display...()` (elles écrivent avec `cout`) : elle utilise
  les méthodes qui retournent des données (`getAllBooks()`, getters…). Le tri se fait en Python.
- `Library` possède ses objets (`unique_ptr`) : les méthodes qui retournent `Book*` / `User*`
  sont exposées avec `return_value_policy::reference_internal` pour que Python ne les détruise pas.
- La journalisation était faite dans `main.cpp` : la GUI appelle donc `ActivityLogger` elle-même.
- Les vérifications manquantes du C++ sont faites dans la GUI : `addBook` n'empêche pas un ISBN
  en double et `removeBook` accepte de supprimer un livre emprunté.
- `createBackup()` lance une exception si un `.backup` existe déjà (`filesystem::copy_file` sans
  écrasement) : la GUI l'attrape et affiche un message au lieu de planter.

## Outils IA utilisés et méthode
- **Claude (claude.ai)**, avec l'accord de l'enseignant : plan de travail (`plan.md`), rédaction
  de `AGENTS.md`, code des liaisons pybind11 (`python/bindings.cpp`), explications, et
  vérification du code produit par opencode à chaque étape.
- **opencode** : `/init` avec Gemma 4 E4B en local (Ollama) a échoué, le modèle (~4B paramètres)
  n'arrivait pas à utiliser ses outils. Les cloud models d'Ollama demandaient des crédits payants.
  J'ai ensuite utilisé le modèle gratuit « Big Pickle » d'opencode pour le test du module et
  tous les écrans de la GUI (sessions 03 à 12 dans `chatsLogs/`).
- **Méthode** : une petite étape à la fois (une étape de `plan.md` = un commit), un prompt précis
  par étape, test dans la fenêtre, export de la session, puis commit fait par moi.

## Ce que j'ai appris en vérifiant l'agent
L'agent a affirmé plusieurs fois que le travail était terminé alors qu'il ne l'était pas
(la « fausse validation » vue en cours) :
- **Onglet Utilisateurs (session 08)** : il a écrit les méthodes mais pas les widgets ; quand je
  lui ai redemandé, il a répondu « Déjà présent… Aucun changement fait », ce qui était faux.
  Il a fallu lui citer les lignes exactes du fichier pour qu'il corrige.
- **Onglet Emprunts (session 09)** : même erreur, et cette fois l'application plantait au démarrage
  (`AttributeError`) parce que `__init__` appelait une méthode qui utilisait des widgets inexistants.
- **Statistiques (session 10)** : le rafraîchissement n'était ajouté qu'à la moitié des endroits demandés.

Conclusion : avec un modèle non SOTA, il faut des étapes courtes, des prompts très précis
(« crée les widgets dans `__init__` »), et toujours relire le fichier et tester avant de commiter.
