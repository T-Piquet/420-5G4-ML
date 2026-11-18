#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "book.h"
#include "filemanager.h"
#include "library.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_py, m) {
    m.doc() = "Module Python minimal pour charger et consulter la bibliothèque.";

    py::class_<Book>(m, "Book")
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("to_string", &Book::toString)
        .def("__repr__", [](const Book& book) {
            return "<Book " + book.getISBN() + ">";
        });

    py::class_<User>(m, "User")
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def("to_string", &User::toString)
        .def("__repr__", [](const User& user) {
            return "<User " + user.getUserId() + ">";
        });

    py::class_<Library, std::unique_ptr<Library>>(m, "Library")
        .def("all_books", [](Library& library) {
            std::vector<Book> books;
            for (Book* book : library.getAllBooks()) {
                books.push_back(*book);
            }
            return books;
        })
        .def("search_books_by_title", [](Library& library, const std::string& title) {
            std::vector<Book> books;
            for (Book* book : library.searchBooksByTitle(title)) {
                books.push_back(*book);
            }
            return books;
        }, py::arg("title"))
        .def("search_books_by_author", [](Library& library, const std::string& author) {
            std::vector<Book> books;
            for (Book* book : library.searchBooksByAuthor(author)) {
                books.push_back(*book);
            }
            return books;
        }, py::arg("author"))
        .def("find_book_by_isbn", [](Library& library, const std::string& isbn)
                -> std::optional<Book> {
            Book* book = library.findBookByISBN(isbn);
            if (book == nullptr) {
                return std::nullopt;
            }
            return *book;
        }, py::arg("isbn"))
        .def("available_books", [](Library& library) {
            std::vector<Book> books;
            for (Book* book : library.getAvailableBooks()) {
                books.push_back(*book);
            }
            return books;
        })
        .def("all_users", [](Library& library) {
            std::vector<User> users;
            for (User* user : library.getAllUsers()) {
                users.push_back(*user);
            }
            return users;
        })
        .def("add_book", [](Library& library,
                            const std::string& title,
                            const std::string& author,
                            const std::string& isbn) {
            if (library.findBookByISBN(isbn) != nullptr) {
                return false;
            }
            library.addBook(Book(title, author, isbn));
            return true;
        }, py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("add_user", [](Library& library,
                            const std::string& name,
                            const std::string& user_id) {
            if (library.findUserById(user_id) != nullptr) {
                return false;
            }
            library.addUser(User(name, user_id));
            return true;
        }, py::arg("name"), py::arg("user_id"))
        .def("check_out_book", &Library::checkOutBook,
             py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))
        .def_property_readonly("total_books", &Library::getTotalBooks)
        .def_property_readonly("available_count", &Library::getAvailableBookCount)
        .def_property_readonly("checked_out_count", &Library::getCheckedOutBookCount)
        .def_property_readonly("users_count", [](Library& library) {
            return library.getAllUsers().size();
        });

    m.def("load_library", [](const std::string& dataDir) {
        auto library = std::make_unique<Library>();
        const std::filesystem::path directory(dataDir);
        FileManager fileManager(
            (directory / "books.txt").string(),
            (directory / "users.txt").string());
        fileManager.loadLibraryData(*library);
        return library;
    }, py::arg("data_dir"), "Charge les livres et les utilisateurs depuis un répertoire de données.");

    m.def("save_library", [](Library& library, const std::string& dataDir) {
        const std::filesystem::path directory(dataDir);
        FileManager fileManager(
            (directory / "books.txt").string(),
            (directory / "users.txt").string());
        return fileManager.saveLibraryData(library);
    }, py::arg("library"), py::arg("data_dir"),
       "Sauvegarde les livres et les utilisateurs dans un répertoire de données.");

    m.def("create_backup", [](const std::string& dataDir) {
        const std::filesystem::path directory(dataDir);
        const std::string booksFile = (directory / "books.txt").string();
        const std::string usersFile = (directory / "users.txt").string();
        FileManager fileManager(booksFile, usersFile);

        if (fileManager.fileExists(booksFile + ".backup") ||
            fileManager.fileExists(usersFile + ".backup")) {
            return false;
        }

        try {
            fileManager.createBackup();
            return true;
        } catch (const std::filesystem::filesystem_error&) {
            return false;
        }
    }, py::arg("data_dir"), "Crée une copie de sauvegarde sans écraser les backups existants.");
}
