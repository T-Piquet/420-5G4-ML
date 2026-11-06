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

// Library owns its Book/User instances through unique_ptr. Returning raw
// pointers to Python is unsafe as soon as removeBook() invalidates them, so
// the collection getters expose copies instead.
std::vector<Book> copyBooks(const std::vector<Book*>& books) {
    std::vector<Book> result;
    result.reserve(books.size());
    for (const Book* book : books) {
        if (book != nullptr) {
            result.push_back(*book);
        }
    }
    return result;
}

std::vector<User> copyUsers(const std::vector<User*>& users) {
    std::vector<User> result;
    result.reserve(users.size());
    for (const User* user : users) {
        if (user != nullptr) {
            result.push_back(*user);
        }
    }
    return result;
}

}  // namespace

PYBIND11_MODULE(bibliotheque_cpp, m) {
    m.doc() = "Bindings Python du systeme de gestion de bibliotheque";
    m.attr("__version__") = "0.1.0";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def("getTitle", &Book::getTitle)
        .def("getAuthor", &Book::getAuthor)
        .def("getISBN", &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId", &Book::getBorrowerId)
        .def("setTitle", &Book::setTitle, py::arg("title"))
        .def("setAuthor", &Book::setAuthor, py::arg("author"))
        .def("setISBN", &Book::setISBN, py::arg("isbn"))
        .def("setAvailability", &Book::setAvailability, py::arg("available"))
        .def("setBorrowerId", &Book::setBorrowerId, py::arg("borrowerId"))
        .def("checkOut", &Book::checkOut, py::arg("borrowerId"))
        .def("returnBook", &Book::returnBook)
        .def("toString", &Book::toString)
        .def("toFileFormat", &Book::toFileFormat)
        .def("fromFileFormat", &Book::fromFileFormat, py::arg("line"));

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("userId"))
        .def("getName", &User::getName)
        .def("getUserId", &User::getUserId)
        .def("getBorrowedBooks", &User::getBorrowedBooks)
        .def("setName", &User::setName, py::arg("name"))
        .def("setUserId", &User::setUserId, py::arg("userId"))
        .def("borrowBook", &User::borrowBook, py::arg("isbn"))
        .def("returnBook", &User::returnBook, py::arg("isbn"))
        .def("hasBorrowedBook", &User::hasBorrowedBook, py::arg("isbn"))
        .def("getNumberOfBorrowedBooks", &User::getNumberOfBorrowedBooks)
        .def("toString", &User::toString)
        .def("toFileFormat", &User::toFileFormat)
        .def("fromFileFormat", &User::fromFileFormat, py::arg("line"));

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("addBook", &Library::addBook, py::arg("book"))
        .def("removeBook", &Library::removeBook, py::arg("isbn"))
        .def("findBookByISBN", &Library::findBookByISBN, py::arg("isbn"),
             py::return_value_policy::reference_internal)
        .def("searchBooksByTitle",
             [](Library& library, const std::string& title) {
                 return copyBooks(library.searchBooksByTitle(title));
             },
             py::arg("title"))
        .def("searchBooksByAuthor",
             [](Library& library, const std::string& author) {
                 return copyBooks(library.searchBooksByAuthor(author));
             },
             py::arg("author"))
        .def("getAvailableBooks",
             [](Library& library) {
                 return copyBooks(library.getAvailableBooks());
             })
        .def("getAllBooks",
             [](Library& library) {
                 return copyBooks(library.getAllBooks());
             })
        .def("addUser", &Library::addUser, py::arg("user"))
        .def("findUserById", &Library::findUserById, py::arg("userId"),
             py::return_value_policy::reference_internal)
        .def("getAllUsers",
             [](Library& library) {
                 return copyUsers(library.getAllUsers());
             })
        .def("checkOutBook", &Library::checkOutBook, py::arg("isbn"), py::arg("userId"))
        .def("returnBook", &Library::returnBook, py::arg("isbn"))
        .def("getTotalBooks", &Library::getTotalBooks)
        .def("getAvailableBookCount", &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("booksFile"), py::arg("usersFile"))
        .def("saveLibraryData", &FileManager::saveLibraryData, py::arg("library"))
        .def("loadLibraryData", &FileManager::loadLibraryData, py::arg("library"))
        .def("createBackup", &FileManager::createBackup)
        .def("fileExists", &FileManager::fileExists, py::arg("filename"));
}
