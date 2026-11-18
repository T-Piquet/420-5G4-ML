#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>

#include "library.h"
#include "filemanager.h"


PYBIND11_MODULE(bibliotheque, m) {
    pybind11::class_<Book>(m, "Book")
        .def(pybind11::init<const std::string&, const std::string&, const std::string&>())
        .def("getTitle", &Book::getTitle)
        .def("getAuthor", &Book::getAuthor)
        .def("getISBN", &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId", &Book::getBorrowerId)
        .def("toString", &Book::toString);

    pybind11::class_<User>(m, "User")
        .def(pybind11::init<const std::string&, const std::string&>())
        .def("getName", &User::getName)
        .def("getUserId", &User::getUserId)
        .def("getBorrowedBooks", &User::getBorrowedBooks)
        .def("toString", &User::toString);

    pybind11::class_<Library>(m, "Library")
        .def(pybind11::init<>())
        .def("addBook", &Library::addBook)
        .def("removeBook", &Library::removeBook)
        .def("findBookByISBN", &Library::findBookByISBN, pybind11::return_value_policy::reference)
        .def("searchBooksByTitle", &Library::searchBooksByTitle, pybind11::return_value_policy::reference)
        .def("searchBooksByAuthor", &Library::searchBooksByAuthor, pybind11::return_value_policy::reference)
        .def("getAllBooks", &Library::getAllBooks, pybind11::return_value_policy::reference)
        .def("getAvailableBooks", &Library::getAvailableBooks, pybind11::return_value_policy::reference)
        .def("addUser", &Library::addUser)
        .def("findUserById", &Library::findUserById, pybind11::return_value_policy::reference)
        .def("getAllUsers", &Library::getAllUsers, pybind11::return_value_policy::reference)
        .def("checkOutBook", &Library::checkOutBook)
        .def("returnBook", &Library::returnBook)
        .def("getTotalBooks", &Library::getTotalBooks)
        .def("getAvailableBookCount", &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    pybind11::class_<FileManager>(m, "FileManager")
        .def(pybind11::init<const std::string&, const std::string&>())
        .def("loadLibraryData", &FileManager::loadLibraryData)
        .def("saveLibraryData", &FileManager::saveLibraryData);
}