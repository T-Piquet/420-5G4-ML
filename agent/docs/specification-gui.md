# Bibliothèque personnelle — spécification de l'interface graphique

Nov 17, 2026 · @vita

## Vue d'ensemble

L'application remplace le menu numéroté du TUI par six écrans graphiques qui lisent et écrivent les mêmes fichiers : `books.txt` et `users.txt` dans le dossier `agent/data`. Ce document décrit ce que montre la maquette « Bibliothèque — GUI », écran par écran.

Le jeu de données de la maquette compte 41 livres (27 disponibles, 14 empruntés) et 25 utilisateurs, dont 14 ont un emprunt en cours.

Principes qui guident les écrans :

- **Choisir plutôt que saisir** : on sélectionne un livre ou un emprunteur dans une liste, sans retaper d'ISBN ni d'ID.
- **Empêcher l'erreur avant de l'afficher** : IDs utilisateur attribués automatiquement, doublons d'ISBN signalés à la saisie, suppression d'un livre emprunté bloquée.
- **Rendre l'état visible** : la barre d'état indique en permanence si des modifications restent à enregistrer.
- **Remplacer « Appuyez sur Entrée pour continuer… »** par des bandeaux, des notifications et des dialogues.

## Navigation et structure commune

Chaque écran partage la même ossature : une barre latérale sombre à gauche, un en-tête avec le titre de la page, la zone de contenu et une barre d'état en pied de page. Sur un écran étroit, la barre latérale passe au-dessus du contenu.

| Zone | Contenu |
| --- | --- |
| Barre latérale | Logo « Bibliothèque personnelle » ; liens Tableau de bord, Catalogue, Utilisateurs, Emprunter / Retourner ; groupe « Données » : Enregistrer, Créer une sauvegarde, Quitter |
| En-tête | Titre de l'écran, recherche par titre ou auteur, bouton principal « Ajouter un livre » |
| Barre d'état | Dossier de données (`agent/data`), fichiers utilisés, état d'enregistrement (« Toutes les modifications sont enregistrées » ou « Modifications non enregistrées », avec le rappel Ctrl+S) |

Les trois actions du groupe « Données » mènent aux dialogues décrits dans la section États.

## Écrans

### Tableau de bord

L'écran d'accueil résume la bibliothèque d'un coup d'œil.

- **Quatre compteurs** : total des livres (41), disponibles (27), empruntés (14), utilisateurs (25, dont 14 avec un emprunt).
- **L'étagère** : un dos coloré par livre, dans l'ordre de `books.txt` ; un livre emprunté laisse un emplacement en pointillé. Le survol affiche le titre.
- **Emprunts en cours** : tableau livre / emprunteur (nom et ID) avec un bouton « Retourner » par ligne.
- **Bandeau d'incohérence** : signale les données contradictoires entre les deux fichiers, avec un lien « Examiner ».
- **Auteurs les plus présents** : barres horizontales (George Sand 6, Victor Hugo 5, Molière 3, Jean Racine 3, Émile Zola 2).
- **Actions rapides** : Emprunter un livre, Ajouter un utilisateur, Créer une sauvegarde.

### Catalogue

La liste complète des livres, filtrable et cherchable.

- Recherche en direct par titre ou auteur, insensible aux accents et à la casse (« hugo », « prince »).
- Filtre segmenté : Tous · 41, Disponibles · 27, Empruntés · 14.
- Colonnes : repère de couleur, titre (lien vers la fiche), auteur, ISBN, statut, actions.
- Statut : badge vert « Disponible » ou badge orange au nom de l'emprunteur.
- Actions : « Prêter » (livre disponible) ou « Retourner » (livre emprunté), plus une icône de suppression.
- État vide : « Aucun livre trouvé », avec un bouton « Ajouter ce livre ».
- Compteur sous le tableau : « N livres affichés sur 41 ».

### Fiche livre et ajout d'un livre

L'écran juxtapose la fiche d'un livre existant et le formulaire d'ajout.

- **Fiche** (exemple : *Les Misérables*, Victor Hugo) : couverture stylisée, titre, auteur, ISBN formaté (978-2-253-09633-7), statut, emprunteur lié à sa fiche utilisateur. Boutons « Retourner le livre », « Modifier », « Supprimer ».
- « Supprimer » est désactivé tant que le livre est emprunté ; une note explique qu'il faut d'abord le retourner pour garder la liste de l'emprunteur à jour.
- **Formulaire d'ajout** : Titre, Auteur, ISBN, tous obligatoires ; le caractère « | » est refusé.
- Validation de l'ISBN : tirets et espaces ignorés, 13 chiffres attendus. Un ISBN déjà présent est signalé en rouge avec un lien vers le livre existant, et « Ajouter le livre » reste désactivé.
- Un badge « Modifications non enregistrées » apparaît dans l'en-tête.

### Emprunter / Retourner

Un parcours en deux étapes, avec un onglet Emprunter et un onglet Retourner (qui affiche le nombre d'emprunts).

1. **Choisir un livre disponible** : liste cherchable des seuls livres disponibles, sans saisie d'ISBN.
2. **Choisir l'emprunteur** : liste cherchable des utilisateurs (initiales, nom, ID, nombre de prêts), avec « + Nouvel utilisateur ».

Un récapitulatif livre + emprunteur précède « Annuler » et « Confirmer l'emprunt ». Une notification confirme chaque action, par exemple « … est de retour sur l'étagère ». Le tableau « Livres actuellement empruntés » permet de retourner un livre depuis le même écran.

### Utilisateurs

Une liste et un panneau de détail côte à côte.

- En-tête : « 25 inscrits · 14 avec un emprunt », recherche par nom ou ID.
- Liste : initiales, nom, ID, nombre de prêts (« aucun prêt », « 1 prêt »…).
- Détail : nom, ID, bouton « Prêter un livre », livres empruntés (titre, auteur, ISBN) avec « Retourner » ; état vide « Aucun livre emprunté pour le moment ».
- Alerte d'incohérence sur la fiche concernée, avec un bouton « Corriger ».
- Formulaire « Ajouter un utilisateur » : le nom seulement ; l'ID est attribué automatiquement, ce qui rend les doublons impossibles.

## États : sauvegarde, confirmations, erreurs

Ce que le TUI imprimait sous « Appuyez sur Entrée pour continuer… » devient un bandeau, une notification ou un dialogue.

| Situation | Forme | Contenu et choix proposés |
| --- | --- | --- |
| Enregistrer | Bandeau, puis notification | « 3 modifications non enregistrées » (1 livre ajouté · 2 emprunts), bouton Enregistrer (Ctrl+S) ; puis « Données enregistrées » avec le nombre de livres et d'utilisateurs écrits |
| Créer une sauvegarde alors qu'une existe déjà | Dialogue | `books.txt.backup` et `users.txt.backup` sont déjà présents. Choix : créer une sauvegarde datée (conserve l'ancienne) ou remplacer l'ancienne ; Annuler / Créer la sauvegarde |
| Quitter avec des modifications | Dialogue | « Enregistrer avant de quitter ? » Choix : Quitter sans enregistrer, Annuler, Enregistrer et quitter |
| Supprimer un livre emprunté | Dialogue | « Supprimer « Les Misérables » ? », rappel de l'emprunteur (Marie Dubois, USR001). Choix : Annuler, Retourner d'abord, Retourner et supprimer |
| Incohérence au chargement | Dialogue | `books.txt` dit *Indiana* emprunté par USR010 ; `users.txt` dit que USR010 a *Corinne*. Choix : Ignorer, Garder Corinne, Garder Indiana |
| Échec d'écriture | Bandeau d'erreur | « Impossible d'écrire books.txt », vérifier les droits sur `agent/data` ; Réessayer |
| Aucun dossier de données | Écran vide | Lancé sans `-d` : choisir un dossier contenant les deux fichiers. Choix : Nouvelle bibliothèque, Ouvrir un dossier… |

## Correspondance menus TUI → GUI

La maquette ne numérote que quatre entrées du menu TUI ; les autres fonctions sont rattachées à leur écran sans numéro.

| Menu TUI | Fonction | Où dans la GUI |
| --- | --- | --- |
| 0 | Quitter | Barre latérale › Quitter, dialogue « Enregistrer avant de quitter ? » |
| 2 | Supprimer un livre | Catalogue (icône) et Fiche livre, dialogue de confirmation |
| 12 | Enregistrer | Barre latérale › Enregistrer, Ctrl+S, bandeau de modifications |
| 13 | Créer une sauvegarde | Barre latérale et actions rapides, dialogue de sauvegarde |
| — | Ajouter, rechercher, lister les livres | Catalogue et formulaire d'ajout |
| — | Emprunter, retourner | Emprunter / Retourner, Catalogue, Utilisateurs, Tableau de bord |
| — | Ajouter, lister les utilisateurs | Utilisateurs |

## Identité visuelle et accessibilité

L'identité évoque une bibliothèque en bois et papier : fond crème, barre latérale brun très foncé, accent bordeaux.

| Rôle | Valeur |
| --- | --- |
| Fond de page | #F5EFE3 (crème) |
| Cartes et champs | #FBF8F2 |
| Texte principal, barre latérale | #2A211C |
| Texte secondaire | #6B5D52 |
| Accent, bouton principal | #7A2E2A (survol #5A1F1C) |
| Disponible | texte #1E5A55 sur #DCEBE6 |
| Emprunté, avertissement | texte #8A4A12 sur #F6E3CC |
| Erreur | #9A2B26 |
| Titres | Source Serif 4, 500–600 |
| Texte courant | Inter, 400–600, 14 px |
| ISBN | police à chasse fixe |

Accessibilité prévue dans la maquette :

- Cibles cliquables d'au moins 44 px de haut.
- Icônes décoratives masquées aux lecteurs d'écran ; boutons à icône seule avec un libellé (« Supprimer « Titre » »).
- Champs reliés à leur libellé, erreur signalée par `aria-invalid` et un message associé.
- Statuts distingués par la couleur, une icône et un texte, jamais par la couleur seule.
- Mise en page fluide : la barre latérale et les grilles se replient sur un écran étroit, les tableaux larges défilent dans leur cadre.
