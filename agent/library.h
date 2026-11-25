#ifndef LIBRARY_H
#define LIBRARY_H

#include <vector>
#include <memory>
#include <stdexcept>

#include "book.h"
#include "user.h"

using namespace std;

// Erreur de règle métier, traduite en StoreError par l'adaptateur Python.
class LibraryError : public runtime_error {
public:
    using runtime_error::runtime_error;
};

class Library {
private:
    vector<unique_ptr<Book>> books;
    vector<unique_ptr<User>> users;

public:
    // Constructor and destructor
    Library();
    ~Library() = default;
    
    // Book management
    void addBook(const Book& book);
    Book createBook(const string& title, const string& author, const string& isbn);
    bool removeBook(const string& isbn);
    Book* findBookByISBN(const string& isbn);
    vector<Book*> searchBooksByTitle(const string& title);
    vector<Book*> searchBooksByAuthor(const string& author);
    vector<Book*> searchBooks(const string& query);
    vector<Book*> getAvailableBooks();
    vector<Book*> getAllBooks();
    
    // User management
    void addUser(const User& user);
    User createUser(const string& name);
    bool removeUser(const string& userId);
    User* findUserById(const string& userId);
    vector<User*> getAllUsers();
    
    // Library operations
    bool checkOutBook(const string& isbn, const string& userId);
    Book checkOutBookChecked(const string& isbn, const string& userId);
    bool returnBook(const string& isbn);
    Book returnBookChecked(const string& isbn);
    
    // Display methods
    void displayAllBooks();
    void displayAvailableBooks();
    void displayAllUsers();
    
    // Statistics
    int getTotalBooks() const;
    int getAvailableBookCount() const;
    int getCheckedOutBookCount() const;
};

#endif
