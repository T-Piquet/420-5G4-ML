#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "session.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_py, m) {
    m.doc() = "Façade Python du système de gestion de bibliothèque";

    py::class_<Book>(m, "Book")
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("__repr__", [](const Book& book) {
            return "<Book " + book.getTitle() + " (" + book.getISBN() + ")>";
        });

    py::class_<User>(m, "User")
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def("__repr__", [](const User& user) {
            return "<User " + user.getName() + " (" + user.getUserId() + ")>";
        });

    py::class_<LibrarySession>(m, "LibrarySession")
        .def(py::init<const std::string&>(), py::arg("data_dir"))
        .def("reload", &LibrarySession::reload)
        .def("add_book", &LibrarySession::add_book,
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def("remove_book", &LibrarySession::remove_book, py::arg("isbn"))
        .def("search_books_by_title", &LibrarySession::search_books_by_title, py::arg("text"))
        .def("search_books_by_author", &LibrarySession::search_books_by_author, py::arg("text"))
        .def("get_all_books", &LibrarySession::get_all_books)
        .def("get_available_books", &LibrarySession::get_available_books)
        .def("add_user", &LibrarySession::add_user, py::arg("name"), py::arg("user_id"))
        .def("get_all_users", &LibrarySession::get_all_users)
        .def("check_out_book", &LibrarySession::check_out_book,
             py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &LibrarySession::return_book, py::arg("isbn"))
        .def("stats", &LibrarySession::stats)
        .def("save", &LibrarySession::save)
        .def("backup", &LibrarySession::backup)
        .def_property_readonly("messages", &LibrarySession::get_messages)
        .def("clear_messages", &LibrarySession::clear_messages);
}
