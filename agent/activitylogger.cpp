#include <chrono>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

#include "activitylogger.h"

using namespace std;

ActivityLogger::ActivityLogger(const string& fileName) : logFileName(fileName){}

//Date et Heure actuelles au format 2026-12-23 10:23:57
string ActivityLogger::timeStamp() const {
    time_t now = chrono::system_clock::to_time_t(chrono::system_clock::now());
    tm localTime = *localtime(&now);
    ostringstream oss;
    oss << put_time(&localTime,"%Y-%m-%d %H:%M:%S" );
    return oss.str();
}

void ActivityLogger::log(const string& action, const string& details){
    ofstream file(logFileName, ios::app);
    if(!file.is_open()){
        cout << "Avertissement : impossible d'écrire dans le journal" << logFileName << "\n";
        return;
    }else{
        file << timeStamp() << " - [" << action <<"]"<< details << "\n";
    }
    
}

void ActivityLogger::logBook(const string& action, const Book& book, const string& personName){
    string details = book.getTitle() + "|" + book.getAuthor() + "|" + book.getISBN()
    +"|" + (book.getAvailability() ? "1":"0") + "|" + personName;
    
    log(action,details);
}