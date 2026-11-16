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

# Partie 3 : Interface graphique

## Outils IA utilisés
- **opencode + Ollama (Gemma 4 E4B, local)** : essais de `/init` et de planification
  (voir `chatsLogs/`). Le modèle local, trop petit (~4B paramètres), n'arrivait pas
  à utiliser ses outils pour lire le projet.
- **Claude (claude.ai)**, avec l'accord:    planification (`plan.md`),
  rédaction de `AGENTS.md`, explications et une partie du code.