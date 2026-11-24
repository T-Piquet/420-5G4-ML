#ifndef ACTIVITYLOG_H
#define ACTIVITYLOG_H

#include <filesystem>
#include <fstream>
#include <string>

class Book;
class Library;
std::string activityBookDetails(const Book& book, Library& library);

class ActivityLog {
public:
    explicit ActivityLog(const std::filesystem::path& path);
    void record(const char* action, const std::string& bookDetails);

private:
    std::ofstream file;
};

#endif
