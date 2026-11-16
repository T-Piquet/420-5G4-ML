#include <pybind11/pybind11.h>
#include "../book.h"

namespace py = pybind11;

// Crée un module Python appelé "biblio"
PYBIND11_MODULE(biblio, m) {
    // Rend la classe C++ Book utilisable en Python sous le nom "Book"
    py::class_<Book>(m, "Book")
        .def(py::init<>())   // Book()
        .def(py::init<const std::string&, const std::string&, const std::string&>())  // Book(titre, auteur, isbn)
        .def("getTitle", &Book::getTitle)
        .def("getAuthor", &Book::getAuthor)
        .def("getISBN", &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId", &Book::getBorrowerId)
        .def("toString", &Book::toString);
}