#include "activitylog.h"
#include "library.h"

#include <ctime>
#include <iomanip>
#include <iostream>

std::string activityBookDetails(const Book& book, Library& library) {
    Book snapshot = book;
    if (!book.getAvailability()) {
        const User* borrower = library.findUserById(book.getBorrowerId());
        if (borrower && !borrower->getName().empty()) {
            snapshot.setBorrowerId(borrower->getName());
        }
    }
    return snapshot.toFileFormat();
}

ActivityLog::ActivityLog(const std::filesystem::path& path)
    : file(path, std::ios::app) {
    if (!file) {
        std::cerr << "Erreur : impossible d'ouvrir le journal d'activités " << path << ".\n";
    }
}

void ActivityLog::record(const char* action, const std::string& bookDetails) {
    if (!file) {
        return;
    }
    const std::time_t now = std::time(nullptr);
    const std::tm* localTime = std::localtime(&now);
    if (!localTime) {
        std::cerr << "Erreur : impossible d'horodater l'activité.\n";
        return;
    }
    file << std::put_time(localTime, "%Y-%m-%d %H:%M:%S")
         << " - [" << action << "] " << bookDetails << '\n' << std::flush;
    if (!file) {
        std::cerr << "Erreur : impossible d'écrire dans le journal d'activités.\n";
    }
}
