#include <fstream>
#include <iostream>
#include <filesystem>
#include <system_error>
#include "filemanager.h"

using namespace std;

namespace fs = std::filesystem;

namespace {

// Lignes du fichier des livres, au format attendu par Book::fromFileFormat.
vector<string> bookLines(Library& library) {
    vector<string> lines;
    auto books = library.getAllBooks();
    lines.reserve(books.size());
    for (Book* book : books) {
        lines.push_back(book->toFileFormat());
    }
    return lines;
}

// Lignes du fichier des utilisateurs.
vector<string> userLines(Library& library) {
    vector<string> lines;
    auto users = library.getAllUsers();
    lines.reserve(users.size());
    for (User* user : users) {
        lines.push_back(user->toFileFormat());
    }
    return lines;
}

} // namespace

// Constructor
FileManager::FileManager(const string& booksFile, const string& usersFile)
    : booksFileName(booksFile), usersFileName(usersFile) {}

// Indique si les fichiers de persistance sont configurés
bool FileManager::hasPersistence() const {
    return !booksFileName.empty() && !usersFileName.empty();
}

// Save all library data
bool FileManager::saveLibraryData(Library& library) {
    if (!hasPersistence()) {
        return false; // Mode mémoire : rien à sauvegarder, aucun message d'erreur.
    }

    // Les deux fichiers sont écrits avant le premier rename : une erreur
    // d'écriture (disque plein, permission) laisse les deux originaux intacts.
    const string booksTemp = booksFileName + ".tmp";
    const string usersTemp = usersFileName + ".tmp";

    if (!writeLinesToTemp(booksTemp, bookLines(library))) {
        return false;
    }

    if (!writeLinesToTemp(usersTemp, userLines(library))) {
        error_code ignored;
        fs::remove(booksTemp, ignored);
        return false;
    }

    if (!replaceFile(booksTemp, booksFileName)) {
        error_code ignored;
        fs::remove(usersTemp, ignored);
        return false;
    }

    return replaceFile(usersTemp, usersFileName);
}

// Load all library data
bool FileManager::loadLibraryData(Library& library) {
    if (!hasPersistence()) {
        return false; // Mode mémoire : rien à charger.
    }
    bool booksLoaded = loadBooksFromFile(library);
    bool usersLoaded = loadUsersFromFile(library);
    return booksLoaded || usersLoaded; // Return true if at least one file was loaded
}

// Save books to file
bool FileManager::saveBooksToFile(Library& library) {
    if (!hasPersistence()) {
        return false;
    }
    return saveFileAtomically(booksFileName, bookLines(library));
}

// Save users to file
bool FileManager::saveUsersToFile(Library& library) {
    if (!hasPersistence()) {
        return false;
    }
    return saveFileAtomically(usersFileName, userLines(library));
}

// Load books from file
bool FileManager::loadBooksFromFile(Library& library) {
    ifstream file(booksFileName);
    if (!file.is_open()) {
        cout << "Aucun fichier de livres existant trouvé. Démarrage avec une bibliothèque vide.\n";
        return false;
    }
    
    string line;
    int count = 0;
    while (getline(file, line)) {
        if (!line.empty()) {
            Book book;
            book.fromFileFormat(line);
            library.addBook(book);
            count++;
        }
    }
    
    file.close();
    cout << "Chargé " << count << " livre(s) depuis le fichier.\n";
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
    int count = 0;
    while (getline(file, line)) {
        if (!line.empty()) {
            User user;
            user.fromFileFormat(line);
            library.addUser(user);
            count++;
        }
    }
    
    file.close();
    cout << "Chargé " << count << " utilisateur(s) depuis le fichier.\n";
    return true;
}

// Check if file exists
bool FileManager::fileExists(const string& filename) {
    ifstream file(filename);
    return file.good();
}

// Crée une sauvegarde des fichiers courants, en écrasant la précédente.
bool FileManager::createBackup() {
    if (!hasPersistence()) {
        return false; // Mode mémoire : l'appelant affiche le message adapté.
    }

    const bool booksExist = fileExists(booksFileName);
    const bool usersExist = fileExists(usersFileName);
    if (!booksExist && !usersExist) {
        cout << "Aucun fichier à sauvegarder.\n";
        return false;
    }

    const string booksBackup = booksFileName + ".backup";
    const string usersBackup = usersFileName + ".backup";
    const string booksTemp = booksBackup + ".tmp";
    const string usersTemp = usersBackup + ".tmp";

    // Les deux copies sont préparées avant de remplacer les backups existants,
    // pour ne pas détruire une sauvegarde valide si la seconde copie échoue.
    if (booksExist && !copyFileToTemp(booksFileName, booksTemp)) {
        return false;
    }

    if (usersExist && !copyFileToTemp(usersFileName, usersTemp)) {
        if (booksExist) {
            error_code ignored;
            fs::remove(booksTemp, ignored);
        }
        return false;
    }

    if (booksExist && !replaceFile(booksTemp, booksBackup)) {
        if (usersExist) {
            error_code ignored;
            fs::remove(usersTemp, ignored);
        }
        return false;
    }

    if (usersExist && !replaceFile(usersTemp, usersBackup)) {
        return false;
    }

    cout << "Fichiers de sauvegarde créés.\n";
    return true;
}

// Écrit les lignes dans un fichier temporaire et vérifie que tout est sur disque.
bool FileManager::writeLinesToTemp(const string& tempPath, const vector<string>& lines) {
    ofstream file(tempPath, ios::out | ios::trunc);
    if (!file.is_open()) {
        cout << "Erreur : impossible d'ouvrir " << tempPath << " en écriture.\n";
        return false;
    }

    for (const string& line : lines) {
        file << line << "\n";
    }
    file.flush();

    if (!file) {
        cout << "Erreur : écriture incomplète dans " << tempPath << ".\n";
        file.close();
        error_code ignored;
        fs::remove(tempPath, ignored);
        return false;
    }

    file.close();
    if (!file) {
        cout << "Erreur : fermeture impossible de " << tempPath << ".\n";
        error_code ignored;
        fs::remove(tempPath, ignored);
        return false;
    }

    return true;
}

// Remplace la cible par le temporaire, en conservant ses permissions.
bool FileManager::replaceFile(const string& tempPath, const string& targetPath) {
    error_code statusError;
    const fs::file_status targetStatus = fs::status(targetPath, statusError);
    if (!statusError && fs::exists(targetStatus)) {
        // L'échec de copie des permissions ne doit pas empêcher le remplacement.
        error_code ignored;
        fs::permissions(tempPath, targetStatus.permissions(), ignored);
    }

    error_code renameError;
    fs::rename(tempPath, targetPath, renameError);
    if (renameError) {
        cout << "Erreur : impossible de remplacer " << targetPath
             << " (" << renameError.message() << ").\n";
        error_code ignored;
        fs::remove(tempPath, ignored);
        return false;
    }

    return true;
}

// Sauvegarde un fichier unique de façon atomique.
bool FileManager::saveFileAtomically(const string& path, const vector<string>& lines) {
    const string tempPath = path + ".tmp";
    if (!writeLinesToTemp(tempPath, lines)) {
        return false;
    }
    return replaceFile(tempPath, path);
}

// Copie source vers un temporaire, sans toucher à la cible.
bool FileManager::copyFileToTemp(const string& source, const string& tempPath) {
    error_code copyError;
    fs::copy_file(source, tempPath, fs::copy_options::overwrite_existing, copyError);
    if (copyError) {
        cout << "Erreur : impossible de copier " << source << " vers " << tempPath
             << " (" << copyError.message() << ").\n";
        error_code ignored;
        fs::remove(tempPath, ignored);
        return false;
    }
    return true;
}
