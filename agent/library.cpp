#include <iostream>
#include <algorithm>
#include <cctype>

#include "library.h"

using namespace std;

namespace {

// Minuscule ASCII, sûre pour les octets non signés des chaînes UTF-8.
string toLower(const string& value) {
    string lower = value;
    transform(lower.begin(), lower.end(), lower.begin(),
        [](unsigned char character) {
            return static_cast<char>(tolower(character));
        });
    return lower;
}

} // namespace

// Constructor
Library::Library() {}

// Add book to library
void Library::addBook(const Book& book) {
    books.push_back(make_unique<Book>(book));
}

// Crée un livre en refusant un ISBN déjà présent.
Book Library::createBook(const string& title, const string& author, const string& isbn) {
    if (findBookByISBN(isbn) != nullptr) {
        throw LibraryError("Un livre avec l'ISBN " + isbn + " existe déjà.");
    }

    Book book(title, author, isbn);
    addBook(book);
    return *books.back();
}

// Remove book from library
bool Library::removeBook(const string& isbn) {
    auto it = find_if(books.begin(), books.end(),
        [&isbn](const unique_ptr<Book>& book) {
            return book->getISBN() == isbn;
        });
    
    if (it != books.end()) {
        books.erase(it);
        // Retire l'ISBN des listes d'emprunt pour éviter des références orphelines.
        for (auto& user : users) {
            user->returnBook(isbn);
        }
        return true;
    }
    return false;
}

// Find book by ISBN
Book* Library::findBookByISBN(const string& isbn) {
    auto it = find_if(books.begin(), books.end(),
        [&isbn](const unique_ptr<Book>& book) {
            return book->getISBN() == isbn;
        });
    
    return (it != books.end()) ? it->get() : nullptr;
}

// Search books by title (case-insensitive partial match)
vector<Book*> Library::searchBooksByTitle(const string& title) {
    vector<Book*> results;
    string lowerTitle = toLower(title);
    
    for (auto& book : books) {
        string bookTitle = toLower(book->getTitle());
        
        if (bookTitle.find(lowerTitle) != string::npos) {
            results.push_back(book.get());
        }
    }
    return results;
}

// Search books by author (case-insensitive partial match)
vector<Book*> Library::searchBooksByAuthor(const string& author) {
    vector<Book*> results;
    string lowerAuthor = toLower(author);
    
    for (auto& book : books) {
        string bookAuthor = toLower(book->getAuthor());
        
        if (bookAuthor.find(lowerAuthor) != string::npos) {
            results.push_back(book.get());
        }
    }
    return results;
}

// Recherche un livre par titre ou auteur, dans l'ordre de la bibliothèque.
vector<Book*> Library::searchBooks(const string& query) {
    vector<Book*> results;
    const string needle = toLower(query);

    for (auto& book : books) {
        if (toLower(book->getTitle()).find(needle) != string::npos ||
            toLower(book->getAuthor()).find(needle) != string::npos) {
            results.push_back(book.get());
        }
    }
    return results;
}

// Get all available books
vector<Book*> Library::getAvailableBooks() {
    vector<Book*> available;
    for (auto& book : books) {
        if (book->getAvailability()) {
            available.push_back(book.get());
        }
    }
    return available;
}

// Get all books
vector<Book*> Library::getAllBooks() {
    vector<Book*> allBooks;
    for (auto& book : books) {
        allBooks.push_back(book.get());
    }
    return allBooks;
}

// Add user to library
void Library::addUser(const User& user) {
    users.push_back(make_unique<User>(user));
}

// Crée un utilisateur avec le prochain identifiant libre au format USRXXX.
User Library::createUser(const string& name) {
    vector<int> numbers;
    for (const auto& user : users) {
        const string id = user->getUserId();
        if (id.size() == 6 && id.compare(0, 3, "USR") == 0 &&
            all_of(id.begin() + 3, id.end(), [](unsigned char character) {
                return isdigit(character) != 0;
            })) {
            numbers.push_back(stoi(id.substr(3)));
        }
    }

    int number = numbers.empty() ? 1 : *max_element(numbers.begin(), numbers.end()) + 1;
    while (number <= 999) {
        const string digits = to_string(number);
        const string candidate = "USR" + string(3 - digits.size(), '0') + digits;
        if (findUserById(candidate) == nullptr) {
            break;
        }
        number++;
    }

    if (number > 999) {
        throw LibraryError("Impossible de générer un identifiant unique au format USRXXX.");
    }

    const string digits = to_string(number);
    const string userId = "USR" + string(3 - digits.size(), '0') + digits;
    User user(name, userId);
    addUser(user);
    return *users.back();
}

// Supprime un utilisateur s'il n'a aucun emprunt en cours
bool Library::removeUser(const string& userId) {
    auto it = find_if(users.begin(), users.end(),
        [&userId](const unique_ptr<User>& user) {
            return user->getUserId() == userId;
        });

    if (it == users.end()) {
        return false;
    }

    // Refus tant que l'utilisateur a des livres empruntés.
    if (!(*it)->getBorrowedBooks().empty()) {
        return false;
    }

    // Refus si un livre le désigne encore comme emprunteur (données incohérentes).
    for (const auto& book : books) {
        if (book->getBorrowerId() == userId) {
            return false;
        }
    }

    users.erase(it);
    return true;
}

// Find user by ID
User* Library::findUserById(const string& userId) {
    auto it = find_if(users.begin(), users.end(),
        [&userId](const unique_ptr<User>& user) {
            return user->getUserId() == userId;
        });
    
    return (it != users.end()) ? it->get() : nullptr;
}

// Get all users
vector<User*> Library::getAllUsers() {
    vector<User*> allUsers;
    for (auto& user : users) {
        allUsers.push_back(user.get());
    }
    return allUsers;
}

// Check out book
bool Library::checkOutBook(const string& isbn, const string& userId) {
    Book* book = findBookByISBN(isbn);
    User* user = findUserById(userId);
    
    if (book && user && book->getAvailability()) {
        book->checkOut(user->getUserId());
        user->borrowBook(isbn);
        return true;
    }
    return false;
}

// Emprunte un livre en expliquant précisément le refus.
Book Library::checkOutBookChecked(const string& isbn, const string& userId) {
    Book* book = findBookByISBN(isbn);
    if (book == nullptr) {
        throw LibraryError("Livre introuvable.");
    }

    User* user = findUserById(userId);
    if (user == nullptr) {
        throw LibraryError("Utilisateur introuvable.");
    }

    if (!book->getAvailability()) {
        throw LibraryError("Ce livre est déjà emprunté.");
    }

    book->checkOut(user->getUserId());
    user->borrowBook(isbn);
    return *book;
}

// Return book
bool Library::returnBook(const string& isbn) {
    Book* book = findBookByISBN(isbn);
    
    if (book && !book->getAvailability()) {
        // Find the user who borrowed this book
        for (auto& user : users) {
            if (user->hasBorrowedBook(isbn)) {
                user->returnBook(isbn);
                break;
            }
        }
        book->returnBook();
        return true;
    }
    return false;
}

// Retourne un livre en expliquant précisément le refus.
Book Library::returnBookChecked(const string& isbn) {
    Book* book = findBookByISBN(isbn);
    if (book == nullptr) {
        throw LibraryError("Livre introuvable.");
    }

    if (book->getAvailability()) {
        throw LibraryError("Ce livre n'est pas emprunté.");
    }

    returnBook(isbn);
    return *book;
}

// Display all books
void Library::displayAllBooks() {
    if (books.empty()) {
        cout << "Aucun livre dans la bibliothèque.\n";
        return;
    }
    
    cout << "\n=== TOUS LES LIVRES ===\n";
    for (size_t i = 0; i < books.size(); ++i) {
        cout << "\nLivre " << (i + 1) << " :\n";
        cout << books[i]->toString() << "\n";
        cout << "-------------------------\n";
    }
}

// Display available books
void Library::displayAvailableBooks() {
    auto available = getAvailableBooks();
    
    if (available.empty()) {
        cout << "Aucun livre disponible pour emprunt.\n";
        return;
    }
    
    cout << "\n=== LIVRES DISPONIBLES ===\n";
    for (size_t i = 0; i < available.size(); ++i) {
        cout << "\nLivre " << (i + 1) << " :\n";
        cout << available[i]->toString() << "\n";
        cout << "---------------------------\n";
    }
}

// Display all users
void Library::displayAllUsers() {
    if (users.empty()) {
        cout << "Aucun utilisateur enregistré.\n";
        return;
    }
    
    cout << "\n=== TOUS LES UTILISATEURS ===\n";
    for (size_t i = 0; i < users.size(); ++i) {
        cout << "\nUtilisateur " << (i + 1) << " :\n";
        cout << users[i]->toString() << "\n";
        cout << "------------------------------\n";
    }
}

// Statistics
int Library::getTotalBooks() const { return books.size(); }
int Library::getAvailableBookCount() const {
    return count_if(books.begin(), books.end(),
        [](const unique_ptr<Book>& book) {
            return book->getAvailability();
        });
}
int Library::getCheckedOutBookCount() const { return getTotalBooks() - getAvailableBookCount(); }