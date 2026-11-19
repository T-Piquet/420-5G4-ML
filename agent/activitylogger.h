#ifndef ACTIVITYLOGGER_H
#define ACTIVITYLOGGER_H

#include <string>

#include "book.h"

using namespace std;

class ActivityLogger {
private: 
    string logFileName;

    string timeStamp() const;

public:
    explicit ActivityLogger(const string& fileName);   

    void log(const string& action, const string& details);

    void logBook(const string& action, const Book& book, const string& personName = "");

};
#endif