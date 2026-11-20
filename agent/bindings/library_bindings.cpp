// Liaison pybind11 entre le cœur C++ et l'interface Python.
//
// Le module expose les classes existantes sans les modifier : la bibliothèque
// reste la source de vérité pour l'état et la persistance. Les accesseurs
// renvoient des copies afin qu'aucun pointeur interne ne puisse devenir
// invalide après une suppression ou un rechargement.

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

namespace {

std::vector<Book> copyBooks(const std::vector<Book*>& books) {
    std::vector<Book> copies;
    copies.reserve(books.size());
    for (Book* book : books) {
        copies.push_back(*book);
    }
    return copies;
}

std::vector<User> copyUsers(const std::vector<User*>& users) {
    std::vector<User> copies;
    copies.reserve(users.size());
    for (User* user : users) {
        copies.push_back(*user);
    }
    return copies;
}

} // namespace

PYBIND11_MODULE(bibliotheque_core, module) {
    module.doc() =
        "Cœur C++ de la bibliothèque personnelle exposé à l'interface Python.";

    py::class_<Book>(module, "Book")
        .def(py::init<>())
        .def(
            py::init<const std::string&, const std::string&, const std::string&>(),
            py::arg("title"),
            py::arg("author"),
            py::arg("isbn"))
        .def_property("title", &Book::getTitle, &Book::setTitle)
        .def_property("author", &Book::getAuthor, &Book::setAuthor)
        .def_property("isbn", &Book::getISBN, &Book::setISBN)
        .def_property(
            "available", &Book::getAvailability, &Book::setAvailability)
        .def_property(
            "borrower_id", &Book::getBorrowerId, &Book::setBorrowerId)
        .def("check_out", &Book::checkOut, py::arg("borrower_id"))
        .def("return_book", &Book::returnBook)
        .def("to_file_format", &Book::toFileFormat)
        .def("from_file_format", &Book::fromFileFormat, py::arg("line"));

    py::class_<User>(module, "User")
        .def(py::init<>())
        .def(
            py::init<const std::string&, const std::string&>(),
            py::arg("name"),
            py::arg("user_id"))
        .def_property("name", &User::getName, &User::setName)
        .def_property("user_id", &User::getUserId, &User::setUserId)
        .def_property_readonly("borrowed_isbns", &User::getBorrowedBooks)
        .def("borrow_book", &User::borrowBook, py::arg("isbn"))
        .def("return_book", &User::returnBook, py::arg("isbn"))
        .def("has_borrowed_book", &User::hasBorrowedBook, py::arg("isbn"))
        .def("borrowed_count", &User::getNumberOfBorrowedBooks)
        .def("to_file_format", &User::toFileFormat)
        .def("from_file_format", &User::fromFileFormat, py::arg("line"));

    py::class_<Library>(module, "Library")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def(
            "find_book",
            [](Library& library, const std::string& isbn) -> std::optional<Book> {
                Book* book = library.findBookByISBN(isbn);
                if (book == nullptr) {
                    return std::nullopt;
                }
                return *book;
            },
            py::arg("isbn"))
        .def("add_user", &Library::addUser, py::arg("user"))
        .def(
            "find_user",
            [](Library& library, const std::string& user_id) -> std::optional<User> {
                User* user = library.findUserById(user_id);
                if (user == nullptr) {
                    return std::nullopt;
                }
                return *user;
            },
            py::arg("user_id"))
        .def(
            "all_books",
            [](Library& library) { return copyBooks(library.getAllBooks()); })
        .def(
            "all_users",
            [](Library& library) { return copyUsers(library.getAllUsers()); })
        .def(
            "available_books",
            [](Library& library) {
                return copyBooks(library.getAvailableBooks());
            })
        .def(
            "search_by_title",
            [](Library& library, const std::string& title) {
                return copyBooks(library.searchBooksByTitle(title));
            },
            py::arg("title"))
        .def(
            "search_by_author",
            [](Library& library, const std::string& author) {
                return copyBooks(library.searchBooksByAuthor(author));
            },
            py::arg("author"))
        .def(
            "check_out_book",
            &Library::checkOutBook,
            py::arg("isbn"),
            py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def("total_books", &Library::getTotalBooks)
        .def("available_count", &Library::getAvailableBookCount)
        .def("checked_out_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(module, "FileManager")
        .def(
            py::init<const std::string&, const std::string&>(),
            py::arg("books_file"),
            py::arg("users_file"))
        .def("load_library", &FileManager::loadLibraryData, py::arg("library"))
        .def("save_library", &FileManager::saveLibraryData, py::arg("library"))
        .def("load_books", &FileManager::loadBooksFromFile, py::arg("library"))
        .def("save_books", &FileManager::saveBooksToFile, py::arg("library"))
        .def("load_users", &FileManager::loadUsersFromFile, py::arg("library"))
        .def("save_users", &FileManager::saveUsersToFile, py::arg("library"))
        .def("file_exists", &FileManager::fileExists, py::arg("filename"))
        .def("create_backup", &FileManager::createBackup);
}
