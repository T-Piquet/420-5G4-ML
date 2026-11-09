// python_bindings.cpp - Liaisons pybind11 pour le système de bibliothèque C++.
//
// Les listes et recherches renvoient des copies : un objet Python ne peut donc
// jamais pointer vers un livre ou un utilisateur supprimé côté C++. Toute
// modification de l'état passe par les méthodes de Library.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

namespace {

template <typename T>
std::vector<T> copyAll(const std::vector<T*>& items) {
    std::vector<T> copies;
    copies.reserve(items.size());
    for (const T* item : items) {
        copies.push_back(*item);
    }
    return copies;
}

template <typename T>
std::optional<T> copyIfFound(const T* item) {
    return item ? std::optional<T>(*item) : std::nullopt;
}

}  // namespace

PYBIND11_MODULE(bibliotheque, m) {
    m.doc() = "Système de gestion de bibliothèque C++.";

    py::class_<Book>(m, "Book", "Un livre du catalogue.")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def("get_title", &Book::getTitle, "Retourne le titre du livre.")
        .def("get_author", &Book::getAuthor, "Retourne l'auteur du livre.")
        .def("get_isbn", &Book::getISBN, "Retourne l'ISBN du livre.")
        .def("is_available", &Book::getAvailability, "Indique si le livre est disponible.")
        .def("get_borrower_id", &Book::getBorrowerId,
             "Retourne l'identifiant de l'emprunteur, ou une chaîne vide.")
        .def("set_title", &Book::setTitle, py::arg("title"))
        .def("set_author", &Book::setAuthor, py::arg("author"))
        .def("set_isbn", &Book::setISBN, py::arg("isbn"))
        .def("check_out",
             [](Book& book, const std::string& borrowerId) {
                 if (!book.getAvailability()) {
                     return false;
                 }
                 book.checkOut(borrowerId);
                 return true;
             },
             py::arg("borrower_id"),
             "Emprunte cet objet. Retourne False s'il est déjà emprunté.")
        .def("return_book", &Book::returnBook, "Rend cet objet disponible.")
        .def("to_file_format", &Book::toFileFormat)
        .def("__str__", &Book::toString);

    py::class_<User>(m, "User", "Un adhérent de la bibliothèque.")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(), py::arg("name"),
             py::arg("user_id"))
        .def("get_name", &User::getName, "Retourne le nom de l'adhérent.")
        .def("get_user_id", &User::getUserId, "Retourne l'identifiant de l'adhérent.")
        .def("get_borrowed_books", &User::getBorrowedBooks,
             "Retourne les ISBN empruntés par l'adhérent.")
        .def("get_number_of_borrowed_books", &User::getNumberOfBorrowedBooks)
        .def("set_name", &User::setName, py::arg("name"))
        .def("set_user_id", &User::setUserId, py::arg("user_id"))
        .def("borrow_book", &User::borrowBook, py::arg("isbn"))
        .def("return_book", &User::returnBook, py::arg("isbn"))
        .def("has_borrowed_book", &User::hasBorrowedBook, py::arg("isbn"))
        .def("to_file_format", &User::toFileFormat)
        .def("__len__", &User::getNumberOfBorrowedBooks)
        .def("__str__", &User::toString);

    py::class_<Library>(m, "Library", "Catalogue, adhérents et emprunts.")
        .def(py::init<>())
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"),
             "Supprime un livre disponible. Retourne False s'il est absent ou emprunté.")
        .def("find_book_by_isbn",
             [](Library& lib, const std::string& isbn) {
                 return copyIfFound(lib.findBookByISBN(isbn));
             },
             py::arg("isbn"), "Retourne le livre ayant exactement cet ISBN, ou None.")
        .def("search_by_title",
             [](Library& lib, const std::string& title) {
                 return copyAll(lib.searchBooksByTitle(title));
             },
             py::arg("title"), "Recherche partielle par titre.")
        .def("search_by_author",
             [](Library& lib, const std::string& author) {
                 return copyAll(lib.searchBooksByAuthor(author));
             },
             py::arg("author"), "Recherche partielle par auteur.")
        .def("get_available_books",
             [](Library& lib) { return copyAll(lib.getAvailableBooks()); })
        .def("get_all_books", [](Library& lib) { return copyAll(lib.getAllBooks()); })
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("find_user_by_id",
             [](Library& lib, const std::string& userId) {
                 return copyIfFound(lib.findUserById(userId));
             },
             py::arg("user_id"), "Retourne l'adhérent ayant exactement cet identifiant, ou None.")
        .def("get_all_users", [](Library& lib) { return copyAll(lib.getAllUsers()); })
        .def("checkout_book", &Library::checkOutBook, py::arg("isbn"), py::arg("user_id"),
             "Emprunte un livre pour un adhérent. Retourne True si réussi.")
        .def("return_book", &Library::returnBook, py::arg("isbn"),
             "Retourne un livre emprunté. Retourne True si réussi.")
        .def("get_total_books", &Library::getTotalBooks)
        .def("get_available_book_count", &Library::getAvailableBookCount)
        .def("get_checked_out_book_count", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager", "Lecture et écriture des fichiers de données.")
        .def(py::init<const std::string&, const std::string&>(), py::arg("books_file"),
             py::arg("users_file"))
        .def("load_data", &FileManager::loadLibraryData, py::arg("library"))
        .def("save_data", &FileManager::saveLibraryData, py::arg("library"))
        .def("save_books", &FileManager::saveBooksToFile, py::arg("library"))
        .def("save_users", &FileManager::saveUsersToFile, py::arg("library"))
        .def("load_books", &FileManager::loadBooksFromFile, py::arg("library"))
        .def("load_users", &FileManager::loadUsersFromFile, py::arg("library"))
        .def("file_exists", &FileManager::fileExists, py::arg("filename"))
        .def("create_backup", &FileManager::createBackup,
             "Copie les fichiers enregistrés vers leurs fichiers .backup.");

    m.def("create_library",
          [](const std::string& booksFile, const std::string& usersFile) {
              auto library = std::make_unique<Library>();
              FileManager fileManager(booksFile, usersFile);
              fileManager.loadLibraryData(*library);
              return library;
          },
          py::arg("books_file"), py::arg("users_file"),
          "Crée une bibliothèque chargée depuis les fichiers.");
}
