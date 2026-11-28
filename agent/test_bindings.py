from bibliotheque_cpp import Book, User, Library, FileManager
from tempfile import TemporaryDirectory
from pathlib import Path

library = Library()

# Ajout
book = Book("1984", "George Orwell", "123456")
user = User("Utilisateur Test", "U001")

library.addBook(book)
library.addUser(user)

assert library.getTotalBooks() == 1
assert library.getAvailableBookCount() == 1
assert len(library.getAllUsers()) == 1
print("OK - Ajout")

# Recherche
assert library.findBookByISBN("123456").getTitle() == "1984"
assert len(library.searchBooksByTitle("1984")) == 1
assert len(library.searchBooksByAuthor("George Orwell")) == 1
print("OK - Recherche")

# Emprunt
assert library.checkOutBook("123456", "U001")
assert library.getCheckedOutBookCount() == 1
assert library.getAvailableBookCount() == 0
print("OK - Emprunt")

# Retour
assert library.returnBook("123456")
assert library.getAvailableBookCount() == 1
print("OK - Retour")

# Persistance
with TemporaryDirectory() as dossier:
    books = str(Path(dossier) / "books.txt")
    users = str(Path(dossier) / "users.txt")

    manager = FileManager(books, users)
    assert manager.saveLibraryData(library)

    nouvelle_library = Library()
    assert manager.loadLibraryData(nouvelle_library)
    assert nouvelle_library.getTotalBooks() == 1
    assert len(nouvelle_library.getAllUsers()) == 1

print("OK - Sauvegarde et chargement")

# Suppression
assert library.removeBook("123456")
assert library.getTotalBooks() == 0
print("OK - Suppression")

print("Tous les tests ont réussi !")
