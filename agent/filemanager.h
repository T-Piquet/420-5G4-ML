#ifndef FILEMANAGER_H
#define FILEMANAGER_H

#include <functional>
#include <iostream>
#include <string>

#include "library.h"

using namespace std;

class FileManager {
private:
    string booksFileName;
    string usersFileName;
    function<void(const string&)> report;

public:
    // Constructor (le rapporteur par défaut garde les messages du CLI)
    FileManager(const string& booksFile, const string& usersFile,
                function<void(const string&)> reporter =
                    [](const string& message) { cout << message << '\n'; });
    
    // File operations
    bool saveLibraryData(Library& library);
    bool loadLibraryData(Library& library);
    
    // Individual file operations
    bool saveBooksToFile(Library& library);
    bool saveUsersToFile(Library& library);
    bool loadBooksFromFile(Library& library);
    bool loadUsersFromFile(Library& library);
    
    // Utility methods
    bool fileExists(const string& filename);
    void createBackup();
};

#endif
