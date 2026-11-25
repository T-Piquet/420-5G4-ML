#include <optional>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

using namespace std;

namespace {

// Copie les livres possédés par la bibliothèque pour que Python ne conserve
// jamais de pointeur vers un élément supprimé.
vector<Book> copyBooks(const vector<Book*>& books) {
    vector<Book> copies;
    copies.reserve(books.size());
    for (const Book* book : books) {
        copies.push_back(*book);
    }
    return copies;
}

// Même principe pour les utilisateurs.
vector<User> copyUsers(const vector<User*>& users) {
    vector<User> copies;
    copies.reserve(users.size());
    for (const User* user : users) {
        copies.push_back(*user);
    }
    return copies;
}

} // namespace

PYBIND11_MODULE(bibliotheque_core, m) {
    m.doc() = "Liaison pybind11 du moteur C++ de la bibliothèque";
    m.attr("__version__") = "0.1.0";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const string&, const string&, const string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId);

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const string&, const string&>(),
             py::arg("name"), py::arg("user_id"))
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed", &User::getBorrowedBooks);

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("books", [](Library& library) {
            return copyBooks(library.getAllBooks());
        })
        .def("users", [](Library& library) {
            return copyUsers(library.getAllUsers());
        })
        .def("find_book", [](Library& library, const string& isbn) -> optional<Book> {
            const Book* book = library.findBookByISBN(isbn);
            if (book == nullptr) {
                return nullopt;
            }
            return *book;
        }, py::arg("isbn"))
        .def("find_user", [](Library& library, const string& userId) -> optional<User> {
            const User* user = library.findUserById(userId);
            if (user == nullptr) {
                return nullopt;
            }
            return *user;
        }, py::arg("user_id"))
        .def("search_books_by_title", [](Library& library, const string& title) {
            return copyBooks(library.searchBooksByTitle(title));
        }, py::arg("title"))
        .def("search_books_by_author", [](Library& library, const string& author) {
            return copyBooks(library.searchBooksByAuthor(author));
        }, py::arg("author"))
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("remove_user", &Library::removeUser, py::arg("user_id"))
        .def("check_out_book", &Library::checkOutBook,
             py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def_property_readonly("total_books", &Library::getTotalBooks)
        .def_property_readonly("available_book_count", &Library::getAvailableBookCount)
        .def_property_readonly("checked_out_book_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const string&, const string&>(),
             py::arg("books_file"), py::arg("users_file"))
        .def("has_persistence", &FileManager::hasPersistence)
        .def("save_library_data", &FileManager::saveLibraryData, py::arg("library"))
        .def("load_library_data", &FileManager::loadLibraryData, py::arg("library"))
        .def("save_books_to_file", &FileManager::saveBooksToFile, py::arg("library"))
        .def("save_users_to_file", &FileManager::saveUsersToFile, py::arg("library"))
        .def("load_books_from_file", &FileManager::loadBooksFromFile, py::arg("library"))
        .def("load_users_from_file", &FileManager::loadUsersFromFile, py::arg("library"))
        .def("file_exists", &FileManager::fileExists, py::arg("filename"))
        .def("create_backup", &FileManager::createBackup);
}
