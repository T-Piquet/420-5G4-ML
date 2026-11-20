#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "book.h"
#include "user.h"
#include "library.h"
#include "filemanager.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_py, m) {
    m.doc() = "Bindings Python (pybind11) pour le moteur C++ de gestion de bibliothèque";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def("get_title", &Book::getTitle)
        .def("get_author", &Book::getAuthor)
        .def("get_isbn", &Book::getISBN)
        .def("get_availability", &Book::getAvailability)
        .def("is_available", &Book::getAvailability)
        .def("get_borrower_id", &Book::getBorrowerId)
        .def("set_title", &Book::setTitle, py::arg("title"))
        .def("set_author", &Book::setAuthor, py::arg("author"))
        .def("set_isbn", &Book::setISBN, py::arg("isbn"))
        .def("set_availability", &Book::setAvailability, py::arg("available"))
        .def("set_borrower_id", &Book::setBorrowerId, py::arg("borrower_id"))
        .def("check_out", &Book::checkOut, py::arg("borrower_id"))
        .def("return_book", &Book::returnBook)
        .def("to_string", &Book::toString)
        .def("to_file_format", &Book::toFileFormat)
        .def("from_file_format", &Book::fromFileFormat, py::arg("line"))
        .def("__repr__", [](const Book& b) {
            return "<Book titre='" + b.getTitle() + "' isbn='" + b.getISBN() + "'>";
        });

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("user_id"))
        .def("get_name", &User::getName)
        .def("get_user_id", &User::getUserId)
        .def("get_borrowed_books", &User::getBorrowedBooks)
        .def("get_number_of_borrowed_books", &User::getNumberOfBorrowedBooks)
        .def("set_name", &User::setName, py::arg("name"))
        .def("set_user_id", &User::setUserId, py::arg("user_id"))
        .def("borrow_book", &User::borrowBook, py::arg("isbn"))
        .def("return_book", &User::returnBook, py::arg("isbn"))
        .def("has_borrowed_book", &User::hasBorrowedBook, py::arg("isbn"))
        .def("to_string", &User::toString)
        .def("to_file_format", &User::toFileFormat)
        .def("from_file_format", &User::fromFileFormat, py::arg("line"))
        .def("__repr__", [](const User& u) {
            return "<User nom='" + u.getName() + "' id='" + u.getUserId() + "'>";
        });

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("find_book_by_isbn", &Library::findBookByISBN, py::arg("isbn"),
             py::return_value_policy::reference_internal)
        .def("search_books_by_title", &Library::searchBooksByTitle, py::arg("title"),
             py::return_value_policy::reference_internal)
        .def("search_books_by_author", &Library::searchBooksByAuthor, py::arg("author"),
             py::return_value_policy::reference_internal)
        .def("get_available_books", &Library::getAvailableBooks,
             py::return_value_policy::reference_internal)
        .def("get_all_books", &Library::getAllBooks,
             py::return_value_policy::reference_internal)
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("find_user_by_id", &Library::findUserById, py::arg("user_id"),
             py::return_value_policy::reference_internal)
        .def("get_all_users", &Library::getAllUsers,
             py::return_value_policy::reference_internal)
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
