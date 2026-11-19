#include <exception>
#include <filesystem>
#include <utility>

#include "session.h"

using namespace std;

namespace {
string dataFilePath(const string& data_dir, const string& fileName) {
    return (filesystem::path(data_dir) / fileName).string();
}

template <typename T>
vector<T> copyValues(const vector<T*>& values) {
    vector<T> copies;
    copies.reserve(values.size());
    for (T* value : values) {
        copies.push_back(*value);
    }
    return copies;
}
}

LibrarySession::LibrarySession(const string& data_dir)
    : library(make_unique<Library>()),
      fileManager(dataFilePath(data_dir, "books.txt"),
                  dataFilePath(data_dir, "users.txt"),
                  [this](const string& message) { messages.push_back(message); }) {
    reload();
}

bool LibrarySession::reload() {
    messages.clear();
    library = make_unique<Library>();
    return fileManager.loadLibraryData(*library);
}

bool LibrarySession::add_book(const string& title, const string& author, const string& isbn) {
    if (library->findBookByISBN(isbn)) {
        return false;
    }
    library->addBook(Book(title, author, isbn));
    return true;
}

bool LibrarySession::remove_book(const string& isbn) {
    if (!library->findBookByISBN(isbn)) {
        return false;
    }
    return_book(isbn);
    return library->removeBook(isbn);
}

vector<Book> LibrarySession::search_books_by_title(const string& text) const {
    return copyValues(library->searchBooksByTitle(text));
}

vector<Book> LibrarySession::search_books_by_author(const string& text) const {
    return copyValues(library->searchBooksByAuthor(text));
}

vector<Book> LibrarySession::get_all_books() const {
    return copyValues(library->getAllBooks());
}

vector<Book> LibrarySession::get_available_books() const {
    return copyValues(library->getAvailableBooks());
}

bool LibrarySession::add_user(const string& name, const string& user_id) {
    if (library->findUserById(user_id)) {
        return false;
    }
    library->addUser(User(name, user_id));
    return true;
}

vector<User> LibrarySession::get_all_users() const {
    return copyValues(library->getAllUsers());
}

bool LibrarySession::check_out_book(const string& isbn, const string& user_id) {
    return library->checkOutBook(isbn, user_id);
}

bool LibrarySession::return_book(const string& isbn) {
    return library->returnBook(isbn);
}

map<string, int> LibrarySession::stats() const {
    return {
        {"total_books", library->getTotalBooks()},
        {"available_books", library->getAvailableBookCount()},
        {"checked_out_books", library->getCheckedOutBookCount()},
        {"total_users", static_cast<int>(library->getAllUsers().size())}
    };
}

bool LibrarySession::save() {
    return fileManager.saveLibraryData(*library);
}

bool LibrarySession::backup() {
    try {
        fileManager.createBackup();
        return true;
    } catch (const exception&) {
        messages.push_back("Erreur : Impossible de créer la sauvegarde.");
        return false;
    }
}

const vector<string>& LibrarySession::get_messages() const {
    return messages;
}

void LibrarySession::clear_messages() {
    messages.clear();
}
