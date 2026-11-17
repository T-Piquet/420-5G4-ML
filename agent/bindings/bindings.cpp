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

// Les methodes de Library renvoient des pointeurs vers des objets possedes par
// les unique_ptr internes. On renvoie des copies a Python pour eviter tout
// probleme de propriete memoire (double free) cote interpreter.
std::vector<Book> booksAsCopies(const std::vector<Book*>& books) {
    std::vector<Book> copies;
    copies.reserve(books.size());
    for (const Book* book : books) {
        copies.push_back(*book);
    }
    return copies;
}

std::vector<User> usersAsCopies(const std::vector<User*>& users) {
    std::vector<User> copies;
    copies.reserve(users.size());
    for (const User* user : users) {
        copies.push_back(*user);
    }
    return copies;
}

}  // namespace

PYBIND11_MODULE(bibliotheque_py, m) {
    m.doc() = "Bindings pybind11 pour le systeme de gestion de bibliotheque";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("is_available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("__str__", &Book::toString)
        .def("__repr__", [](const Book& book) {
            return "<Book isbn=" + book.getISBN() + ">";
        });

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("user_id"))
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def_property_readonly("number_of_borrowed_books",
                               &User::getNumberOfBorrowedBooks)
        .def("has_borrowed_book", &User::hasBorrowedBook, py::arg("isbn"))
        .def("__str__", &User::toString)
        .def("__repr__", [](const User& user) {
            return "<User id=" + user.getUserId() + ">";
        });

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("book_exists", [](Library& library, const std::string& isbn) {
            return library.findBookByISBN(isbn) != nullptr;
        }, py::arg("isbn"))
        .def("search_books_by_title",
             [](Library& library, const std::string& title) {
                 return booksAsCopies(library.searchBooksByTitle(title));
             }, py::arg("title"))
        .def("search_books_by_author",
             [](Library& library, const std::string& author) {
                 return booksAsCopies(library.searchBooksByAuthor(author));
             }, py::arg("author"))
        .def("get_available_books", [](Library& library) {
            return booksAsCopies(library.getAvailableBooks());
        })
        .def("get_all_books", [](Library& library) {
            return booksAsCopies(library.getAllBooks());
        })
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("user_exists", [](Library& library, const std::string& user_id) {
            return library.findUserById(user_id) != nullptr;
        }, py::arg("user_id"))
        .def("get_all_users", [](Library& library) {
            return usersAsCopies(library.getAllUsers());
        })
        .def("check_out_book", &Library::checkOutBook,
             py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def("get_total_books", &Library::getTotalBooks)
        .def("get_available_book_count", &Library::getAvailableBookCount)
        .def("get_checked_out_book_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("books_file"), py::arg("users_file"))
        .def("load_library_data", &FileManager::loadLibraryData,
             py::arg("library"))
        .def("save_library_data", &FileManager::saveLibraryData,
             py::arg("library"))
        .def("save_books_to_file", &FileManager::saveBooksToFile,
             py::arg("library"))
        .def("save_users_to_file", &FileManager::saveUsersToFile,
             py::arg("library"))
        .def("create_backup", &FileManager::createBackup);
}
