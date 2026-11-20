#include <optional>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "book.h"
#include "user.h"
#include "library.h"
#include "filemanager.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_py, m) {
    m.doc() = "Gestion de bibliotheque personnelle (coeur C++)";

    py::class_<Book>(m, "Book")
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("is_available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("to_string", &Book::toString)
        .def("to_file_format", &Book::toFileFormat);

    py::class_<User>(m, "User")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("user_id"))
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def_property_readonly("borrowed_count", &User::getNumberOfBorrowedBooks)
        .def("to_string", &User::toString);

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("find_book_by_isbn",
             [](Library& library, const std::string& isbn) -> std::optional<Book> {
                 Book* book = library.findBookByISBN(isbn);
                 if (!book) {
                     return std::nullopt;
                 }
                 return *book;
             },
             py::arg("isbn"))
        .def("search_books_by_title",
             [](Library& library, const std::string& query) {
                 std::vector<Book> books;
                 for (Book* book : library.searchBooksByTitle(query)) {
                     books.push_back(*book);
                 }
                 return books;
             },
             py::arg("query"))
        .def("search_books_by_author",
             [](Library& library, const std::string& query) {
                 std::vector<Book> books;
                 for (Book* book : library.searchBooksByAuthor(query)) {
                     books.push_back(*book);
                 }
                 return books;
             },
             py::arg("query"))
        .def("get_available_books",
             [](Library& library) {
                 std::vector<Book> books;
                 for (Book* book : library.getAvailableBooks()) {
                     books.push_back(*book);
                 }
                 return books;
             })
        .def("get_all_books",
             [](Library& library) {
                 std::vector<Book> books;
                 for (Book* book : library.getAllBooks()) {
                     books.push_back(*book);
                 }
                 return books;
             })
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("remove_user", &Library::removeUser, py::arg("user_id"))
        .def("find_user_by_id",
             [](Library& library, const std::string& user_id) -> std::optional<User> {
                 User* user = library.findUserById(user_id);
                 if (!user) {
                     return std::nullopt;
                 }
                 return *user;
             },
             py::arg("user_id"))
        .def("get_all_users",
             [](Library& library) {
                 std::vector<User> users;
                 for (User* user : library.getAllUsers()) {
                     users.push_back(*user);
                 }
                 return users;
             })
        .def("check_out_book", &Library::checkOutBook,
             py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def("total_books", &Library::getTotalBooks)
        .def("available_book_count", &Library::getAvailableBookCount)
        .def("checked_out_book_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("books_file"), py::arg("users_file"))
        .def("load_library_data", &FileManager::loadLibraryData, py::arg("library"))
        .def("save_library_data", &FileManager::saveLibraryData, py::arg("library"))
        .def("create_backup", &FileManager::createBackup)
        .def("file_exists", &FileManager::fileExists, py::arg("filename"));
}
