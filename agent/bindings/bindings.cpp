#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <string>
#include <vector>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

namespace {

std::vector<Book> copyBooks(const std::vector<Book*>& books) {
    std::vector<Book> copies;
    copies.reserve(books.size());
    for (const Book* book : books) {
        copies.push_back(*book);
    }
    return copies;
}

std::vector<User> copyUsers(const std::vector<User*>& users) {
    std::vector<User> copies;
    copies.reserve(users.size());
    for (const User* user : users) {
        copies.push_back(*user);
    }
    return copies;
}

py::object findBook(Library& library, const std::string& isbn) {
    if (Book* book = library.findBookByISBN(isbn)) {
        return py::cast(*book);
    }
    return py::none();
}

py::object findUser(Library& library, const std::string& userId) {
    if (User* user = library.findUserById(userId)) {
        return py::cast(*user);
    }
    return py::none();
}

std::vector<Book> getAllBooks(Library& library) {
    return copyBooks(library.getAllBooks());
}

std::vector<Book> getAvailableBooks(Library& library) {
    return copyBooks(library.getAvailableBooks());
}

std::vector<Book> searchBooksByTitle(Library& library, const std::string& title) {
    return copyBooks(library.searchBooksByTitle(title));
}

std::vector<Book> searchBooksByAuthor(Library& library, const std::string& author) {
    return copyBooks(library.searchBooksByAuthor(author));
}

std::vector<User> getAllUsers(Library& library) {
    return copyUsers(library.getAllUsers());
}

} // namespace

PYBIND11_MODULE(bibliotheque_core, m) {
    m.doc() = "Liaison Python du systeme de gestion de bibliotheque";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("__repr__", [](const Book& book) {
            return "<Book " + book.getISBN() + ">";
        });

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("user_id"))
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def_property_readonly("number_of_borrowed_books", &User::getNumberOfBorrowedBooks)
        .def("has_borrowed_book", &User::hasBorrowedBook, py::arg("isbn"))
        .def("__repr__", [](const User& user) {
            return "<User " + user.getUserId() + ">";
        });

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("find_book_by_isbn", &findBook, py::arg("isbn"))
        .def("search_books_by_title", &searchBooksByTitle, py::arg("title"))
        .def("search_books_by_author", &searchBooksByAuthor, py::arg("author"))
        .def("get_available_books", &getAvailableBooks)
        .def("get_all_books", &getAllBooks)
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("find_user_by_id", &findUser, py::arg("user_id"))
        .def("get_all_users", &getAllUsers)
        .def("check_out_book", &Library::checkOutBook, py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def("get_total_books", &Library::getTotalBooks)
        .def("get_available_book_count", &Library::getAvailableBookCount)
        .def("get_checked_out_book_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("books_file"), py::arg("users_file"))
        .def("save_library_data", &FileManager::saveLibraryData, py::arg("library"))
        .def("load_library_data", &FileManager::loadLibraryData, py::arg("library"))
        .def("save_books_to_file", &FileManager::saveBooksToFile, py::arg("library"))
        .def("save_users_to_file", &FileManager::saveUsersToFile, py::arg("library"))
        .def("load_books_from_file", &FileManager::loadBooksFromFile, py::arg("library"))
        .def("load_users_from_file", &FileManager::loadUsersFromFile, py::arg("library"))
        .def("file_exists", &FileManager::fileExists, py::arg("filename"))
        .def("create_backup", &FileManager::createBackup);
}
