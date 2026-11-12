#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "src/book.h"
#include "src/user.h"
#include "src/library.h"
#include "src/filemanager.h"

namespace py = pybind11;

PYBIND11_MODULE(library_core, m) {
    m.doc() = "Bindings pybind11 pour le systeme de gestion de bibliotheque";

    // ---------- Book ----------
    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        // Getters
        .def("getTitle",        &Book::getTitle)
        .def("getAuthor",       &Book::getAuthor)
        .def("getISBN",         &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId",   &Book::getBorrowerId)
        // Setters
        .def("setTitle",        &Book::setTitle)
        .def("setAuthor",       &Book::setAuthor)
        .def("setISBN",         &Book::setISBN)
        .def("setAvailability", &Book::setAvailability)
        .def("setBorrowerId",   &Book::setBorrowerId)
        // Methods
        .def("checkOut",  &Book::checkOut)
        .def("returnBook", &Book::returnBook)
        .def("toString",  &Book::toString)
        .def("toFileFormat", &Book::toFileFormat)
        .def("fromFileFormat", &Book::fromFileFormat)
        // Proprietes Python (lecture seule, via getters)
        .def_property_readonly("title",        &Book::getTitle)
        .def_property_readonly("author",       &Book::getAuthor)
        .def_property_readonly("isbn",         &Book::getISBN)
        .def_property_readonly("isAvailable",  &Book::getAvailability)
        .def_property_readonly("borrowerId",   &Book::getBorrowerId);

    // ---------- User ----------
    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("userId"))
        .def("getName",                &User::getName)
        .def("getUserId",              &User::getUserId)
        .def("getBorrowedBooks",       &User::getBorrowedBooks)
        .def("setName",                &User::setName)
        .def("setUserId",              &User::setUserId)
        .def("borrowBook",             &User::borrowBook)
        .def("returnBook",             &User::returnBook)
        .def("hasBorrowedBook",        &User::hasBorrowedBook)
        .def("getNumberOfBorrowedBooks",&User::getNumberOfBorrowedBooks)
        .def("toString",               &User::toString)
        .def("toFileFormat",           &User::toFileFormat)
        .def("fromFileFormat",         &User::fromFileFormat)
        .def_property_readonly("name",   &User::getName)
        .def_property_readonly("userId", &User::getUserId);

    // ---------- Library ----------
    // Note: retourne des Book*/User* bruts. On precise
    // return_value_policy::reference_internal pour que Python ne detruise pas
    // les objets (ils appartiennent a Library).
    py::class_<Library>(m, "Library")
        .def(py::init<>())
        // Book management
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
        // User management
        .def("addUser", &Library::addUser)
        .def("findUserById", &Library::findUserById,
             py::return_value_policy::reference_internal)
        .def("getAllUsers", &Library::getAllUsers,
             py::return_value_policy::reference_internal)
        // Library operations
        .def("checkOutBook", &Library::checkOutBook)
        .def("returnBook",   &Library::returnBook)
        // Statistics
        .def("getTotalBooks",          &Library::getTotalBooks)
        .def("getAvailableBookCount",  &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    // ---------- FileManager ----------
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