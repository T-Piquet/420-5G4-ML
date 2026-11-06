// python_bindings.cpp - Pybind11 bindings for the C++ Library System
// Seule les méthodes utiles pour l'utilisation Python sont exposées

#define PYBIND11_MODULE(bibliotheque, m) {
    
    // Bind Book class
    py::class_<Book>(m, "Book", py::buffer_protocol())
        .def(py::init<std::string, std::string, std::string>(),
             py::arg("title"), 
             py::arg("author"), 
             py::arg("isbn"))
        .def_readonly_static("__doc__", R"(
            Book: Représente un objet livre dans le système de bibliothèque.
            
            Attributs:
                title (str): Titre du livre
                author (str): Auteur du livre  
                isbn (str): ISBN unique du livre
                is_available (bool): Disponibilité du livre
            
            Méthodes:
                check_out(idemprunteur, str): Emprunter le livre
                return_book(): Remettre le livre en rayon
        )")
        .def("get_title", &Book::getTitle, 
             py::return_value_policy::copy,
             R"(Retourne le titre du livre.)")
        .def("get_author", &Book::getAuthor, 
             py::return_value_policy::copy,
             R"(Retourne l'auteur du livre.)")
        .def("get_isbn", &Book::getISBN, 
             py::return_value_policy::copy,
             R"(Retourne l'ISBN du livre.)")
        .def("is_available", &Book::getAvailability,
             R"(Vérifie si le livre est disponible (disponible pour emprunt)).")
        .def("check_out", [](Book& book, std::string borrower_id) {
            if (book.getAvailability()) {
                book.setAvailability(false);
                book.setBorrowerId(borrower_id);
                return true;
            }
            return false;
        }, py::arg("borrower_id"),
             R"(Tente d'emprunter le livre. Retourne True si réussi, False si déjà emprunté.)")
        .def("return_book", &Book::returnBook,
             R"(Remet le livre disponible.)");
    
    // Bind User class  
    py::class_<User>(m, "User", py::buffer_protocol())
        .def(py::init<std::string, std::string>(),
             py::arg("name"), 
             py::arg("user_id"))
        .def_readonly_static("__doc__", R"(
            User: Représente un utilisateur de la bibliothèque.
            
            Attributs:
                name (str): Nom de l'utilisateur
                user_id (str): ID unique de l'utilisateur
                borrowed_books (list): Liste des ISBN empruntés
            
            Méthodes:
                borrow_book(isbn, str): Emprunter un livre
                return_book(isbn, str): Remettre un livre
        )")
        .def("get_name", &User::getName, 
             py::return_value_policy::copy,
             R"(Retourne le nom de l'utilisateur.)")
        .def("get_user_id", &User::getUserId, 
             py::return_value_policy::copy,
             R"(Retourne l'ID de l'utilisateur.)")
        .def("borrow_book", &User::borrowBook, py::arg("isbn"),
             R"(Enregistre que l'utilisateur emprunte ce livre.)")
        .def("has_borrowed_book", &User::hasBorrowedBook, py::arg("isbn"),
             py::return_value_policy::copy,
             R"(Vérifie si l'utilisateur a emprunté un livre donné.)")
        .def("__len__", &User::getNumberOfBorrowedBooks,
             R"(Retourne le nombre de livres empruntés.)");
    
    // Bind Library class
    py::class_<Library>(m, "Library", py::buffer_protocol())
        .def(py::init<>(),
             py::return_value_policy::take_ownership)
        .def_readonly_static("__doc__", R"(
            Library: Système de gestion complète de bibliothèque.
            
            Méthodes principales:
                add_book(book, Book): Ajouter un livre au catalogue
                add_user(user, User): Ajouter un nouvel utilisateur
                checkout_book(isbn, user_id, str): Vérifier un livre à un utilisateur
                return_book(isbn, str): Remettre un livre au rayon
                
            Recherche:
                search_by_title(title, str): Recherche par titre (partial match case-insensitive)
                search_by_author(author, str): Recherche par auteur
                get_available_books(): Retourne la liste des livres disponibles
                
            Statistiques:
                total_books(count): Nombre total de livres
                available_books(count): Nombre de livres disponibles
        )")
        .def("add_book", &Library::addBook, py::arg("book"),
             R"(Ajoute un livre au catalogue de la bibliothèque.)")
        .def("add_user", &Library::addUser, py::arg("user"),
             R"(Ajoute un utilisateur au système.)")
        .def("search_by_title", [](const Library& lib, std::string title) -> std::vector<std::unique_ptr<Book>> {
            auto results = lib.searchBooksByTitle(title);
            std::vector<std::unique_ptr<Book>> ret;
            for (auto* b : results) {
                ret.push_back(std::make_unique<Book>(*b));
            }
            return ret;
        }, py::arg("title"),
             R"(Recherche des livres par titre (match partiel insensible à la casse).")
        )
        .def("search_by_author", [](const Library& lib, std::string author) -> std::vector<std::unique_ptr<Book>> {
            auto results = lib.searchBooksByAuthor(author);
            std::vector<std::unique_ptr<Book>> ret;
            for (auto* b : results) {
                ret.push_back(std::make_unique<Book>(*b));
            }
            return ret;
        }, py::arg("author"),
             R"(Recherche des livres par auteur.)")
        .def("get_available_books", [](const Library& lib) -> std::vector<std::unique_ptr<Book>> {
            auto results = lib.getAvailableBooks();
            std::vector<std::unique_ptr<Book>> ret;
            for (auto* b : results) {
                ret.push_back(std::make_unique<Book>(*b));
            }
            return ret;
        }, py::return_value_policy::take_ownership,
             R"(Retourne la liste des livres actuellement disponibles.)")
        .def("get_total_books", [](const Library& lib) {
            return lib.getTotalBooks();
        }, py::return_value_policy::automatic_reference,
             R"(Retourne le nombre total de livres dans la bibliothèque.)")
        .def("checkout_book", &Library::checkOutBook, 
             py::arg("isbn"), py::arg("user_id"),
             R"(Vérifie un livre pour un utilisateur spécifique. Retourne True si réussi.)")
        .def("return_book", &Library::returnBook, 
             py::arg("isbn"),
             R"(Remet un livre disponible au rayon.)");
    
    // Bind FileManager class
    py::class_<FileManager>(m, "FileManager", py::buffer_protocol())
        .def(py::init<std::string, std::string>(),
             py::arg("books_file"), 
             py::arg("users_file"))
        .def_readonly_static("__doc__", R"(
            FileManager: Gestionnaire d'opérations de fichiers pour la bibliothèque.
            
            Utilise des fichiers pipe-separated pour stocker les données:
                books_file: Fichier CSV contenant les livres (id|titra|isbn|auteur|annee)
                users_file: Fichier CSV contenant les utilisateurs
        )")
        .def("load_data", &FileManager::loadLibraryData,
             R"(Charge les données des livres et utilisateurs depuis les fichiers.)")
        .def("save_data", &FileManager::saveLibraryData,
             R"(Sauvegarde toutes les données vers les fichiers.)")
        .def("file_exists", &FileManager::fileExists, py::arg("filename"),
             py::return_value_policy::copy,
             R"(Vérifie si un fichier existe.)");
    
    // Helper functions
    m.def("create_library", [](const std::string& books_file, const std::string& users_file) {
        Library lib;
        FileManager fm(books_file, users_file);
        fm.loadLibraryData(lib);
        return lib;
    }, 
         py::arg("books_file"), py::arg("users_file"),
         R"(Crée un nouvel objet Library chargé depuis les fichiers.)");

}
