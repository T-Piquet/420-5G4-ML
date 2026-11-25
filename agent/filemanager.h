#ifndef FILEMANAGER_H
#define FILEMANAGER_H

#include <string>
#include <vector>

#include "library.h"

using namespace std;

class FileManager {
private:
    string booksFileName;
    string usersFileName;

    // Écriture atomique : les lignes vont dans un fichier temporaire, puis le
    // temporaire remplace la cible par un rename. La cible n'est jamais tronquée.
    bool writeLinesToTemp(const string& tempPath, const vector<string>& lines);
    bool replaceFile(const string& tempPath, const string& targetPath);
    bool saveFileAtomically(const string& path, const vector<string>& lines);

    // Copie source vers tempPath sans toucher à la cible, pour préparer un backup.
    bool copyFileToTemp(const string& source, const string& tempPath);

public:
    // Constructor
    FileManager(const string& booksFile, const string& usersFile);
    
    // État de la persistance : faux si les chemins de fichiers sont vides (mode mémoire)
    bool hasPersistence() const;

    // File operations
    // save/load retournent false en mode mémoire ; utiliser hasPersistence() pour
    // distinguer ce cas d'un échec d'entrée/sortie réel.
    bool saveLibraryData(Library& library);
    bool loadLibraryData(Library& library);
    
    // Individual file operations
    bool saveBooksToFile(Library& library);
    bool saveUsersToFile(Library& library);
    bool loadBooksFromFile(Library& library);
    bool loadUsersFromFile(Library& library);
    
    // Utility methods
    bool fileExists(const string& filename);
    // Backup écrasable : renvoie false en mode mémoire, si aucun fichier n'existe
    // ou si la copie a échoué.
    bool createBackup();
};

#endif
