#!/usr/bin/env python3
"""
Main entry point for the Bibliothèque Library System (Demo Mode)
No C++ server connection - pure memory mode with CSV persistence
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import LibraryModel
from view import create_app


def main():
    """Main entry point"""
    print("📚 Bibliothèque - Interface Démo (Mode Mémoire)")
    print("=" * 50)
    
    # Create model with data directory
    data_dir = "./data"
    model = LibraryModel(data_dir=data_dir)
    
    # Load from CSV files if they exist, or use demo data
    books_file = os.path.join(data_dir, "books.txt")
    users_file = os.path.join(data_dir, "users.txt")
    model.load_from_csv(books_file, users_file)
    
    # If no data loaded, use demo data
    if model.get_book_count() == 0:
        print("📖 Chargement des données démo...")
        demo_books = [
            ("Le Prince et le Moine", "978-2-36804-015-0", "Antoine Volodine", "2024"),
            ("L'Envers du miroir", "978-2-7467-4285-3", "Pierre Michon", "2023"),
            ("Les Fruits de la terre", "978-2-7021-1345-9", "Jean Eustache", "1984"),
        ]
        
        for title, isbn, author, year in demo_books:
            model.add_book(title, isbn, author, year)
        
        print(f"   Ajout de {len(demo_books)} livres démo")
    
    # Create and run the application
    try:
        window, view = create_app(model)
        window.mainloop()
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
