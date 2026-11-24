#include <algorithm>
#include <filesystem>
#include <optional>
#include <stdexcept>
#include <unordered_set>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>

#include "filemanager.h"
#include "activitylog.h"

namespace py = pybind11;
namespace fs = std::filesystem;
using namespace pybind11::literals;

namespace {
fs::path checkedDirectory(const fs::path& directory) {
    if (!fs::is_directory(directory)) {
        throw std::runtime_error("Répertoire de données introuvable : " + directory.string());
    }
    return fs::absolute(directory);
}

class Session {
    fs::path directory;
    Library library;
    FileManager files;
    ActivityLog log;

public:
    explicit Session(const fs::path& path)
        : directory(checkedDirectory(path)),
          files((directory / "books.txt").string(), (directory / "users.txt").string()),
          log(directory / "activity.log") {
        // Missing files mean a new catalog, but an existing unreadable file
        // must not be silently replaced by a later save.
        const auto load = [this](const char* name, auto loader) {
            const auto path = directory / name;
            if (fs::exists(path) && (!fs::is_regular_file(path) || !(files.*loader)(library))) {
                throw std::runtime_error("Impossible de lire : " + path.string());
            }
        };
        load("books.txt", &FileManager::loadBooksFromFile);
        load("users.txt", &FileManager::loadUsersFromFile);
    }

    py::list books(bool available, const std::string& query, std::optional<bool> byAuthor, BookSortOrder order) {
        auto results = available ? library.getAvailableBooks() : library.getAllBooks();
        if (!query.empty()) {
            std::unordered_set<Book*> matches;
            if (!byAuthor.value_or(false)) {
                const auto titles = library.searchBooksByTitle(query);
                matches.insert(titles.begin(), titles.end());
            }
            if (byAuthor.value_or(true)) {
                const auto authors = library.searchBooksByAuthor(query);
                matches.insert(authors.begin(), authors.end());
            }
            results.erase(std::remove_if(results.begin(), results.end(), [&](Book* book) {
                return matches.count(book) == 0;
            }), results.end());
        }
        py::list rows;
        for (const Book* book : Library::sortBooksForDisplay(std::move(results), order)) {
            std::string borrower = book->getBorrowerId();
            if (const auto* user = library.findUserById(borrower); user && !user->getName().empty()) {
                borrower = user->getName();
            }
            rows.append(py::dict("title"_a=book->getTitle(), "author"_a=book->getAuthor(),
                "isbn"_a=book->getISBN(), "available"_a=book->getAvailability(), "borrower"_a=borrower));
        }
        return rows;
    }

    py::list users() {
        py::list rows;
        for (const User* user : library.getAllUsers()) {
            rows.append(py::dict("name"_a=user->getName(), "id"_a=user->getUserId()));
        }
        return rows;
    }

    py::dict statistics() {
        return py::dict("total"_a=library.getTotalBooks(), "available"_a=library.getAvailableBookCount(),
            "borrowed"_a=library.getCheckedOutBookCount(), "users"_a=library.getAllUsers().size());
    }

    void addBook(const std::string& title, const std::string& author, const std::string& isbn) {
        if (library.findBookByISBN(isbn)) {
            throw std::runtime_error("Cet ISBN existe déjà.");
        }
        const Book book(title, author, isbn);
        library.addBook(book);
        log.record("AJOUT LIVRE", activityBookDetails(book, library));
    }

    void addUser(const std::string& name, const std::string& id) {
        if (library.findUserById(id)) {
            throw std::runtime_error("Cet ID utilisateur existe déjà.");
        }
        library.addUser(User(name, id));
    }

    void removeBook(const std::string& isbn) {
        const Book* book = library.findBookByISBN(isbn);
        if (!book) {
            throw std::runtime_error("Livre introuvable.");
        }
        const auto details = activityBookDetails(*book, library);
        library.removeBook(isbn);
        log.record("SUPPRESSION LIVRE", details);
    }

    void borrowBook(const std::string& isbn, const std::string& id) {
        if (!library.checkOutBook(isbn, id)) {
            throw std::runtime_error("Emprunt impossible : vérifiez le livre, sa disponibilité et l’utilisateur.");
        }
        log.record("EMPRUNT", activityBookDetails(*library.findBookByISBN(isbn), library));
    }

    void returnBook(const std::string& isbn) {
        const Book* book = library.findBookByISBN(isbn);
        if (!book || book->getAvailability()) {
            throw std::runtime_error("Ce livre n’est pas emprunté ou est introuvable.");
        }
        const auto details = activityBookDetails(*book, library);
        library.returnBook(isbn);
        log.record("RETOUR", details);
    }

    void save() {
        if (!files.saveLibraryData(library)) {
            throw std::runtime_error("Impossible de sauvegarder les données.");
        }
    }

    void backup() {
        if (!files.fileExists((directory / "books.txt").string()) &&
            !files.fileExists((directory / "users.txt").string())) {
            throw std::runtime_error("Aucun fichier à copier. Sauvegardez d’abord les données.");
        }
        files.createBackup();
    }
};
} // namespace

PYBIND11_MODULE(_bibliotheque, module) {
    py::enum_<BookSortOrder>(module, "BookSortOrder")
        .value("CATALOG", BookSortOrder::Catalog)
        .value("TITLE", BookSortOrder::Title)
        .value("AUTHOR", BookSortOrder::Author);

    py::class_<Session>(module, "Session")
        .def(py::init<const fs::path&>())
        .def("books", &Session::books)
        .def("users", &Session::users)
        .def("statistics", &Session::statistics)
        .def("add_book", &Session::addBook)
        .def("add_user", &Session::addUser)
        .def("remove_book", &Session::removeBook)
        .def("borrow_book", &Session::borrowBook)
        .def("return_book", &Session::returnBook)
        .def("save", &Session::save)
        .def("backup", &Session::backup);

    module.def("list_available_books", [](const fs::path& dataDir, BookSortOrder order) {
        if (!fs::is_directory(dataDir)) {
            throw std::runtime_error("Répertoire de données introuvable : " + dataDir.string());
        }

        const auto booksFile = dataDir / "books.txt";
        Library library;
        FileManager files(booksFile.string(), "");
        if (!fs::is_regular_file(booksFile) || !files.loadBooksFromFile(library)) {
            throw std::runtime_error("Impossible de lire le catalogue : " + booksFile.string());
        }

        py::list rows;
        for (const Book* book : Library::sortBooksForDisplay(library.getAvailableBooks(), order)) {
            py::dict row;
            row["title"] = book->getTitle();
            row["author"] = book->getAuthor();
            row["isbn"] = book->getISBN();
            rows.append(row);
        }
        return rows;
    }, py::arg("data_dir"), py::arg("order") = BookSortOrder::Catalog);
}
