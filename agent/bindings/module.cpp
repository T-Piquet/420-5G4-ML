// Python bindings for the library-management core (Part 3 GUI).
//
// The GUI is a Python application: it serves the web interface and calls into
// the original C++ model through this pybind11 module. Everything the TUI
// knows how to do (load, save, search, check out, return, back up) stays in
// C++; Python only orchestrates screens and JSON.
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

// The core exposes raw pointers into its unique_ptr collections. Python gets
// copies for lists (safe, serialisable) and live references only where a
// mutation is intended (find_* with reference_internal).
std::vector<Book> all_books(Library& library) {
    std::vector<Book> books;
    for (const Book* book : library.getAllBooks()) {
        books.push_back(*book);
    }
    return books;
}

std::vector<User> all_users(Library& library) {
    std::vector<User> users;
    for (const User* user : library.getAllUsers()) {
        users.push_back(*user);
    }
    return users;
}

std::vector<Book> search_by_title(Library& library, const std::string& title) {
    std::vector<Book> books;
    for (const Book* book : library.searchBooksByTitle(title)) {
        books.push_back(*book);
    }
    return books;
}

std::vector<Book> search_by_author(Library& library, const std::string& author) {
    std::vector<Book> books;
    for (const Book* book : library.searchBooksByAuthor(author)) {
        books.push_back(*book);
    }
    return books;
}

std::vector<Book> available_books(Library& library) {
    std::vector<Book> books;
    for (const Book* book : library.getAvailableBooks()) {
        books.push_back(*book);
    }
    return books;
}

}  // namespace

PYBIND11_MODULE(biblio_core, m) {
    m.doc() = "C++ core of the personal-library application (Book, User, Library, FileManager).";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("set_title", &Book::setTitle)
        .def("set_author", &Book::setAuthor)
        .def("check_out", &Book::checkOut)
        .def("return_book", &Book::returnBook)
        .def("__repr__", [](const Book& book) { return "<Book " + book.getISBN() + ">"; });

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(), py::arg("name"), py::arg("user_id"))
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def("borrow_book", &User::borrowBook)
        .def("return_book", &User::returnBook)
        .def("has_borrowed_book", &User::hasBorrowedBook)
        .def("borrowed_count", &User::getNumberOfBorrowedBooks)
        .def("__repr__", [](const User& user) { return "<User " + user.getUserId() + ">"; });

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("add_book", &Library::addBook)
        .def("remove_book", &Library::removeBook)
        .def("find_book", &Library::findBookByISBN, py::return_value_policy::reference_internal)
        .def("find_user", &Library::findUserById, py::return_value_policy::reference_internal)
        .def("add_user", &Library::addUser)
        .def("check_out_book", &Library::checkOutBook)
        .def("return_book", &Library::returnBook)
        .def("all_books", &all_books)
        .def("all_users", &all_users)
        .def("available_books", &available_books)
        .def("search_by_title", &search_by_title)
        .def("search_by_author", &search_by_author)
        .def("total_books", &Library::getTotalBooks)
        .def("available_count", &Library::getAvailableBookCount)
        .def("checked_out_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(), py::arg("books_file"),
             py::arg("users_file"))
        .def("save_library_data", &FileManager::saveLibraryData)
        .def("load_library_data", &FileManager::loadLibraryData)
        .def("save_books", &FileManager::saveBooksToFile)
        .def("save_users", &FileManager::saveUsersToFile)
        .def("load_books", &FileManager::loadBooksFromFile)
        .def("load_users", &FileManager::loadUsersFromFile)
        .def("file_exists", &FileManager::fileExists)
        .def("create_backup", &FileManager::createBackup);
}
