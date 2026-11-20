#include <algorithm>
#include <fstream>
#include <iostream>
#include <filesystem>
#include <system_error>
#include "filemanager.h"

using namespace std;

namespace {

// Écrit les lignes dans un fichier temporaire puis le renomme : une erreur
// d'écriture ne peut pas laisser le fichier de données tronqué.
bool writeLinesAtomically(const string& filename, const vector<string>& lines) {
    if (filename.empty()) {
        return false;
    }

    filesystem::path target(filename);
    filesystem::path temporary = target;
    temporary += ".tmp";

    ofstream file(temporary, ios::out | ios::trunc);
    if (!file.is_open()) {
        return false;
    }

    for (const string& line : lines) {
        file << line << "\n";
    }
    file.flush();
    if (!file.good()) {
        file.close();
        error_code cleanup;
        filesystem::remove(temporary, cleanup);
        return false;
    }
    file.close();

    error_code renameError;
    filesystem::rename(temporary, target, renameError);
    if (renameError) {
        error_code cleanup;
        filesystem::remove(temporary, cleanup);
        return false;
    }
    return true;
}

} // namespace

// Constructor
FileManager::FileManager(const string& booksFile, const string& usersFile)
    : booksFileName(booksFile), usersFileName(usersFile) {}

// Save all library data
bool FileManager::saveLibraryData(Library& library) {
    return saveBooksToFile(library) && saveUsersToFile(library);
}

// Load all library data
bool FileManager::loadLibraryData(Library& library) {
    bool booksLoaded = loadBooksFromFile(library);
    bool usersLoaded = loadUsersFromFile(library);
    return booksLoaded || usersLoaded; // Return true if at least one file was loaded
}

// Save books to file
bool FileManager::saveBooksToFile(Library& library) {
    vector<string> lines;
    auto books = library.getAllBooks();
    lines.reserve(books.size());
    for (Book* book : books) {
        lines.push_back(book->toFileFormat());
    }

    if (!writeLinesAtomically(booksFileName, lines)) {
        cout << "Erreur : Impossible d'écrire " << booksFileName << ".\n";
        return false;
    }
    return true;
}

// Save users to file
bool FileManager::saveUsersToFile(Library& library) {
    vector<string> lines;
    auto users = library.getAllUsers();
    lines.reserve(users.size());
    for (User* user : users) {
        lines.push_back(user->toFileFormat());
    }

    if (!writeLinesAtomically(usersFileName, lines)) {
        cout << "Erreur : Impossible d'écrire " << usersFileName << ".\n";
        return false;
    }
    return true;
}

// Load books from file
bool FileManager::loadBooksFromFile(Library& library) {
    ifstream file(booksFileName);
    if (!file.is_open()) {
        cout << "Aucun fichier de livres existant trouvé. Démarrage avec une bibliothèque vide.\n";
        return false;
    }
    
    string line;
    int loadedCount = 0;
    while (getline(file, line)) {
        // Ignore les lignes incomplètes : il faut au moins titre|auteur|isbn|disponible.
        if (line.empty() || std::count(line.begin(), line.end(), '|') < 3) {
            continue;
        }

        Book book;
        book.fromFileFormat(line);
        if (book.getISBN().empty()) {
            continue;
        }

        library.addBook(book);
        loadedCount++;
    }
    
    file.close();
    cout << "Chargé " << loadedCount << " livre(s) depuis le fichier.\n";
    return true;
}

// Load users from file
bool FileManager::loadUsersFromFile(Library& library) {
    ifstream file(usersFileName);
    if (!file.is_open()) {
        cout << "Aucun fichier d'utilisateurs existant trouvé. Démarrage sans utilisateurs enregistrés.\n";
        return false;
    }
    
    string line;
    int loadedCount = 0;
    while (getline(file, line)) {
        // Ignore les lignes sans identifiant : il faut au moins nom|id.
        if (line.empty() || std::count(line.begin(), line.end(), '|') < 1) {
            continue;
        }

        User user;
        user.fromFileFormat(line);
        if (user.getUserId().empty()) {
            continue;
        }

        library.addUser(user);
        loadedCount++;
    }
    
    file.close();
    cout << "Chargé " << loadedCount << " utilisateur(s) depuis le fichier.\n";
    return true;
}

// Check if file exists
bool FileManager::fileExists(const string& filename) {
    ifstream file(filename);
    return file.good();
}

// Create backup
bool FileManager::createBackup() {
    bool copied = false;
    bool failed = false;

    auto backupFile = [&](const string& filename) {
        if (!fileExists(filename)) {
            return;
        }

        error_code copyError;
        filesystem::copy_file(
            filename,
            filename + ".backup",
            filesystem::copy_options::overwrite_existing,
            copyError);

        if (copyError) {
            failed = true;
            cout << "Erreur : Impossible de créer " << filename << ".backup.\n";
            return;
        }

        copied = true;
    };

    backupFile(booksFileName);
    backupFile(usersFileName);

    if (failed) {
        return false;
    }

    if (!copied) {
        cout << "Erreur : Aucun fichier à sauvegarder.\n";
        return false;
    }

    cout << "Fichiers de sauvegarde créés.\n";
    return true;
}