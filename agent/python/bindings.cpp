#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // NOUVEAU : convertit vector<string> en liste Python
#include "../book.h"
#include "../user.h"           // NOUVEAU
#include "../library.h"
#include "../filemanager.h"
#include "../activitylogger.h"

namespace py = pybind11;

PYBIND11_MODULE(biblio, m) {
    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>())
        .def("getTitle", &Book::getTitle)
        .def("getAuthor", &Book::getAuthor)
        .def("getISBN", &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId", &Book::getBorrowerId)
        .def("toString", &Book::toString);

    // NOUVEAU : la classe User
    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>())   // User(nom, id)
        .def("getName", &User::getName)
        .def("getUserId", &User::getUserId)
        .def("getBorrowedBooks", &User::getBorrowedBooks)
        .def("getNumberOfBorrowedBooks", &User::getNumberOfBorrowedBooks)
        .def("hasBorrowedBook", &User::hasBorrowedBook)
        .def("toString", &User::toString);

        // Library possède les livres (unique_ptr) → reference_internal :
    // Python ne les supprime pas, et la Library reste vivante tant qu'on les utilise
    auto ref = py::return_value_policy::reference_internal;

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("addBook", &Library::addBook)
        .def("removeBook", &Library::removeBook)
        .def("findBookByISBN", &Library::findBookByISBN, ref)
        .def("searchBooksByTitle", &Library::searchBooksByTitle, ref)
        .def("searchBooksByAuthor", &Library::searchBooksByAuthor, ref)
        .def("getAvailableBooks", &Library::getAvailableBooks, ref)
        .def("getAllBooks", &Library::getAllBooks, ref)
        .def("addUser", &Library::addUser)
        .def("findUserById", &Library::findUserById, ref)
        .def("getAllUsers", &Library::getAllUsers, ref)
        .def("generateUserId", &Library::generateUserId)
        .def("checkOutBook", &Library::checkOutBook)
        .def("returnBook", &Library::returnBook)
        .def("getTotalBooks", &Library::getTotalBooks)
        .def("getAvailableBookCount", &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>())
        .def("saveLibraryData", &FileManager::saveLibraryData)
        .def("loadLibraryData", &FileManager::loadLibraryData)
        .def("createBackup", &FileManager::createBackup);

    py::class_<ActivityLogger>(m, "ActivityLogger")
        .def(py::init<const std::string&>())
        .def("log", &ActivityLogger::log)
        .def("logBook", &ActivityLogger::logBook,
             py::arg("action"), py::arg("book"), py::arg("personName") = "");
}