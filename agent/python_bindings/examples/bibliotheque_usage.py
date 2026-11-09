#!/usr/bin/env python3
"""
Exemple d'utilisation du module Bibliotheque Python.

Cet exemple démontre l'usage des classes Book, User, Library et FileManager.
"""

import sys
import os

# Ajouter le répertoire parent au path pour trouver le module compilé
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bibliotheque import Book, User, Library, FileManager


def main():
    print("=" * 60)
    print("📚 Bibliothèque System - Exemple Python")
    print("=" * 60)
    
    # Créer une instance de la bibliothèque
    fm = FileManager("../data/books.txt", "../data/users.txt")
    
    # Vérifier si les fichiers existes
    if fm.file_exists("../data/books.txt"):
        print("\n✅ Les fichiers de données sont disponibles.")
        
        # Charger la bibliothèque depuis les fichiers
        print("\n📖 Chargement de la bibliothèque...")
        library = create_library("../data/books.txt", "../data/users.txt")
    else:
        print("\n⚠️  Fichiers de données introuvables. Création d'exemple manuel...")
        
        # Créer quelques livres manuellement
        book1 = Book("Le Petit Prince", "Saint-Exupéry, Antoine de", "9780062300268")
        book2 = Book("Les Misérables", "Hugo, Victor", "9782253901106")
        book3 = Book("1984", "Orwell, George", "9780451524935")
        
        library = Library()
        library.add_book(book1)
        library.add_book(book2)
        library.add_book(book3)
    
    # Créer des utilisateurs
    user1 = User("Alice Martin", "alice.martin@email.com")
    user2 = User("Bob Dupont", "bob.dupont@email.com")
    
    library.add_user(user1)
    library.add_user(user2)
    
    print(f"\n📊 Statistiques de la bibliothèque:")
    print(f"  - Total livres: {library.get_total_books()}")
    
    # Remet les livres disponibles (le nombre)
    available_count = len(library.get_available_books())
    print(f"  - Livres disponibles: {available_count}")
    
    # Afficher les livres disponibles
    print("\n📚 Liste des livres disponibles:")
    available_books = library.get_available_books()
    for book in available_books:
        print(f"  • {book.get_title()} de {book.get_author()}")
    
    if not available_books:
        print("    (Aucun livre disponible)")
    
    # Recherche par titre
    print("\n🔍 Recherche de livres contenant 'Le':")
    search_results = library.search_by_title("Le")
    count1 = len(search_results)
    for book in search_results:
        print(f"  • {book.get_title()} (ISBN: {book.get_isbn()})")
    
    if not search_results:
        print("    (Aucun livre trouvé)")
    
    # Vérifier la disponibilité du premier livre
    if len(available_books) > 0 and available_books[0].is_available():
        book_to_checkout = available_books[0]
        
        print(f"\n✅ {book_to_checkout.get_title()} est disponible")
        
        # Prêt le livre à user2
        print("📤 Prêt du livre à un utilisateur...")
        success = library.checkout_book(book_to_checkout.get_isbn(), user2.get_user_id())
        
        if success:
            print(f"    ✅ Livre prêté ! Utilisateur : {user2.get_name()[:15]}...")
            
            # Vérifier l'historique d'emprunt
            if user2.has_borrowed_book(book_to_checkout.get_isbn()):
                borrowed_count = len(user2)
                print(f"    ℹ️ L'utilisateur a emprunté {borrowed_count} livre(s)")
        else:
            print(f"    ❌ Échec du prêt")
        
        # Remettre le livre
        print("\n📥 Remise du livre au rayon...")
        if library.return_book(book_to_checkout.get_isbn()):
            print(f"    ✅ Livre remis et disponible à nouveau")
    
    # Sauvegarder les données
    print("\n💾 Sauvegarde des données...")
    try:
        fm.save_data()
        print("    Données sauvegardées dans data/books.txt et data/users.txt")
    except Exception as e:
        print(f"    ⚠️  Échec de la sauvegarde : {e}")


def create_library(books_file, users_file):
    """Helper pour créer une bibliothèque chargée depuis les fichiers."""
    lib = Library()
    fm = FileManager(books_file, users_file)
    fm.load_data(lib)
    return lib


if __name__ == "__main__":
    main()
