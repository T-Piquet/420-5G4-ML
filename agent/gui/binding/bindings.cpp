#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_core, m) {
    m.doc() = "Bindings pybind11 du système de gestion de bibliothèque personnelle.";

    py::class_<Book>(m, "Book")
        .def(py::init<>(), "Construit un livre vide.")
        .def(py::init<const std::string &, const std::string &, const std::string &>(),
             py::arg("titre"), py::arg("auteur"), py::arg("isbn"),
             "Construit un livre disponible.")
        .def("getTitle", &Book::getTitle, "Retourne le titre du livre.")
        .def("getAuthor", &Book::getAuthor, "Retourne l'auteur du livre.")
        .def("getISBN", &Book::getISBN, "Retourne l'ISBN du livre.")
        .def("getAvailability", &Book::getAvailability,
             "Indique si le livre est disponible.")
        .def("getBorrowerId", &Book::getBorrowerId,
             "Retourne l'identifiant de l'emprunteur.")
        .def("toString", &Book::toString, "Retourne une description lisible du livre.")
        .def("toFileFormat", &Book::toFileFormat,
             "Retourne la représentation du livre au format fichier.")
        .def("fromFileFormat", &Book::fromFileFormat, py::arg("ligne"),
             "Charge le livre depuis une ligne au format fichier.");

    py::class_<User>(m, "User")
        .def(py::init<>(), "Construit un utilisateur vide.")
        .def(py::init<const std::string &, const std::string &>(),
             py::arg("nom"), py::arg("id"),
             "Construit un utilisateur sans emprunt.")
        .def("getName", &User::getName, "Retourne le nom de l'utilisateur.")
        .def("getUserId", &User::getUserId, "Retourne l'identifiant de l'utilisateur.")
        .def("getBorrowedBooks", &User::getBorrowedBooks,
             "Retourne les ISBN des livres empruntés.")
        .def("getNumberOfBorrowedBooks", &User::getNumberOfBorrowedBooks,
             "Retourne le nombre de livres empruntés.")
        .def("hasBorrowedBook", &User::hasBorrowedBook, py::arg("isbn"),
             "Indique si l'utilisateur a emprunté ce livre.")
        .def("toString", &User::toString,
             "Retourne une description lisible de l'utilisateur.")
        .def("toFileFormat", &User::toFileFormat,
             "Retourne la représentation de l'utilisateur au format fichier.")
        .def("fromFileFormat", &User::fromFileFormat, py::arg("ligne"),
             "Charge l'utilisateur depuis une ligne au format fichier.");

    py::class_<Library>(m, "Library")
        .def(py::init<>(), "Construit une bibliothèque vide.")
        .def("addBook", &Library::addBook, py::arg("livre"), "Ajoute un livre.")
        .def("removeBook", &Library::removeBook, py::arg("isbn"),
             "Supprime un livre par son ISBN.")
        .def("findBookByISBN", &Library::findBookByISBN, py::arg("isbn"),
             py::return_value_policy::reference_internal,
             "Retourne le livre correspondant à l'ISBN, ou None.")
        .def("searchBooksByTitle", &Library::searchBooksByTitle, py::arg("titre"),
             py::return_value_policy::reference_internal,
             "Recherche les livres dont le titre contient la chaîne donnée.")
        .def("searchBooksByAuthor", &Library::searchBooksByAuthor, py::arg("auteur"),
             py::return_value_policy::reference_internal,
             "Recherche les livres dont l'auteur contient la chaîne donnée.")
        .def("getAvailableBooks", &Library::getAvailableBooks,
             py::return_value_policy::reference_internal,
             "Retourne les livres disponibles.")
        .def("getAllBooks", &Library::getAllBooks,
             py::return_value_policy::reference_internal,
             "Retourne tous les livres.")
        .def("addUser", &Library::addUser, py::arg("utilisateur"),
             "Ajoute un utilisateur.")
        .def("findUserById", &Library::findUserById, py::arg("id"),
             py::return_value_policy::reference_internal,
             "Retourne l'utilisateur correspondant à l'identifiant, ou None.")
        .def("getAllUsers", &Library::getAllUsers,
             py::return_value_policy::reference_internal,
             "Retourne tous les utilisateurs.")
        .def("checkOutBook", &Library::checkOutBook, py::arg("isbn"), py::arg("id"),
             "Emprunte un livre pour un utilisateur.")
        .def("returnBook", &Library::returnBook, py::arg("isbn"),
             "Retourne un livre emprunté.")
        .def("getTotalBooks", &Library::getTotalBooks,
             "Retourne le nombre total de livres.")
        .def("getAvailableBookCount", &Library::getAvailableBookCount,
             "Retourne le nombre de livres disponibles.")
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount,
             "Retourne le nombre de livres empruntés.");

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string &, const std::string &>(),
             py::arg("fichier_livres"), py::arg("fichier_utilisateurs"),
             "Construit un gestionnaire de fichiers pour les deux fichiers de données.")
        .def("saveLibraryData", &FileManager::saveLibraryData, py::arg("bibliotheque"),
             "Sauvegarde les livres et les utilisateurs.")
        .def("loadLibraryData", &FileManager::loadLibraryData, py::arg("bibliotheque"),
             "Charge les livres et les utilisateurs.")
        .def("saveBooksToFile", &FileManager::saveBooksToFile, py::arg("bibliotheque"),
             "Sauvegarde uniquement les livres.")
        .def("saveUsersToFile", &FileManager::saveUsersToFile, py::arg("bibliotheque"),
             "Sauvegarde uniquement les utilisateurs.")
        .def("loadBooksFromFile", &FileManager::loadBooksFromFile, py::arg("bibliotheque"),
             "Charge uniquement les livres.")
        .def("loadUsersFromFile", &FileManager::loadUsersFromFile, py::arg("bibliotheque"),
             "Charge uniquement les utilisateurs.")
        .def("fileExists", &FileManager::fileExists, py::arg("nom_fichier"),
             "Indique si un fichier existe.")
        .def("createBackup", &FileManager::createBackup,
             "Crée une copie de sauvegarde des fichiers de données.");
}
