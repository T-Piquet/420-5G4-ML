#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // NOUVEAU : convertit vector<string> en liste Python
#include "../book.h"
#include "../user.h"           // NOUVEAU

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
}