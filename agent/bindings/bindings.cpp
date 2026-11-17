#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "book.h"
#include "user.h"
#include "library.h"
#include "filemanager.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_cpp, m) {
    m.doc() = "Bindings pybind11 pour le système de gestion de bibliothèque C++";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def("getTitle", &Book::getTitle)
        .def("getAuthor", &Book::getAuthor)
        .def("getISBN", &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId", &Book::getBorrowerId)
        .def("setTitle", &Book::setTitle)
        .def("setAuthor", &Book::setAuthor)
        .def("setISBN", &Book::setISBN)
        .def("setAvailability", &Book::setAvailability)
        .def("setBorrowerId", &Book::setBorrowerId)
        .def("checkOut", &Book::checkOut)
        .def("returnBook", &Book::returnBook)
        .def("toString", &Book::toString);

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("userId"))
        .def("getName", &User::getName)
        .def("getUserId", &User::getUserId)
        .def("getBorrowedBooks", &User::getBorrowedBooks)
        .def("setName", &User::setName)
        .def("setUserId", &User::setUserId)
        .def("borrowBook", &User::borrowBook)
        .def("returnBook", &User::returnBook)
        .def("hasBorrowedBook", &User::hasBorrowedBook)
        .def("getNumberOfBorrowedBooks", &User::getNumberOfBorrowedBooks)
        .def("toString", &User::toString);

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("addBook", &Library::addBook)
        .def("removeBook", &Library::removeBook)
        .def("findBookByISBN", &Library::findBookByISBN,
             py::return_value_policy::reference_internal)
        .def("searchBooksByTitle", &Library::searchBooksByTitle,
             py::return_value_policy::reference_internal)
        .def("searchBooksByAuthor", &Library::searchBooksByAuthor,
             py::return_value_policy::reference_internal)
        .def("getAvailableBooks", &Library::getAvailableBooks,
             py::return_value_policy::reference_internal)
        .def("getAllBooks", &Library::getAllBooks,
             py::return_value_policy::reference_internal)
        .def("addUser", &Library::addUser)
        .def("findUserById", &Library::findUserById,
             py::return_value_policy::reference_internal)
        .def("getAllUsers", &Library::getAllUsers,
             py::return_value_policy::reference_internal)
        .def("checkOutBook", &Library::checkOutBook)
        .def("returnBook", &Library::returnBook)
        .def("getTotalBooks", &Library::getTotalBooks)
        .def("getAvailableBookCount", &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("booksFile"), py::arg("usersFile"))
        .def("saveLibraryData", &FileManager::saveLibraryData)
        .def("loadLibraryData", &FileManager::loadLibraryData)
        .def("saveBooksToFile", &FileManager::saveBooksToFile)
        .def("saveUsersToFile", &FileManager::saveUsersToFile)
        .def("loadBooksFromFile", &FileManager::loadBooksFromFile)
        .def("loadUsersFromFile", &FileManager::loadUsersFromFile)
        .def("fileExists", &FileManager::fileExists)
        .def("createBackup", &FileManager::createBackup);
}
