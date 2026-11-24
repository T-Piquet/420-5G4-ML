#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <optional>
#include <string>
#include <vector>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

using namespace std;

namespace {

// La bibliothèque possède ses livres et utilisateurs via des unique_ptr.
// On renvoie des copies vers Python pour éviter tout pointeur invalide côté interface.
vector<Book> copyBooks(const vector<Book*>& books) {
    vector<Book> copies;
    copies.reserve(books.size());

    for (const Book* book : books) {
        if (book != nullptr) {
            copies.push_back(*book);
        }
    }

    return copies;
}

vector<User> copyUsers(const vector<User*>& users) {
    vector<User> copies;
    copies.reserve(users.size());

    for (const User* user : users) {
        if (user != nullptr) {
            copies.push_back(*user);
        }
    }

    return copies;
}

optional<Book> findBookCopy(Library& library, const string& isbn) {
    const Book* book = library.findBookByISBN(isbn);

    if (book == nullptr) {
        return nullopt;
    }

    return *book;
}

optional<User> findUserCopy(Library& library, const string& userId) {
    const User* user = library.findUserById(userId);

    if (user == nullptr) {
        return nullopt;
    }

    return *user;
}

}  // namespace

PYBIND11_MODULE(bibliotheque_py, m) {
    m.doc() = "Bindings Python du gestionnaire de bibliothèque C++.";

    py::class_<Book>(m, "Book", "Un livre de la bibliothèque.")
        .def(py::init<>(), "Crée un livre vide.")
        .def(py::init<const string&, const string&, const string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"),
             "Crée un livre disponible.")
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("__repr__", [](const Book& book) {
            return "<Book " + book.getTitle() + " (" + book.getISBN() + ")>";
        });

    py::class_<User>(m, "User", "Un utilisateur de la bibliothèque.")
        .def(py::init<>(), "Crée un utilisateur vide.")
        .def(py::init<const string&, const string&>(),
             py::arg("name"), py::arg("user_id"),
             "Crée un utilisateur avec son nom et son identifiant.")
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def("has_borrowed", &User::hasBorrowedBook, py::arg("isbn"))
        .def("__repr__", [](const User& user) {
            return "<User " + user.getName() + " (" + user.getUserId() + ")>";
        });

    py::class_<Library>(m, "Library", "Collection de livres et d'utilisateurs.")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("find_book", &findBookCopy, py::arg("isbn"))
        .def("all_books", [](Library& library) {
            return copyBooks(library.getAllBooks());
        })
        .def("available_books", [](Library& library) {
            return copyBooks(library.getAvailableBooks());
        })
        .def("search_by_title", [](Library& library, const string& title) {
            return copyBooks(library.searchBooksByTitle(title));
        }, py::arg("title"))
        .def("search_by_author", [](Library& library, const string& author) {
            return copyBooks(library.searchBooksByAuthor(author));
        }, py::arg("author"))
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("find_user", &findUserCopy, py::arg("user_id"))
        .def("all_users", [](Library& library) {
            return copyUsers(library.getAllUsers());
        })
        .def("checkout", &Library::checkOutBook, py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def_property_readonly("total_books", &Library::getTotalBooks)
        .def_property_readonly("available_count", &Library::getAvailableBookCount)
        .def_property_readonly("checked_out_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager", "Lecture et écriture des données de la bibliothèque.")
        .def(py::init<const string&, const string&>(),
             py::arg("books_file"), py::arg("users_file"))
        .def("load", &FileManager::loadLibraryData, py::arg("library"))
        .def("save", &FileManager::saveLibraryData, py::arg("library"))
        .def("backup", &FileManager::createBackup)
        .def("file_exists", &FileManager::fileExists, py::arg("filename"));
}
