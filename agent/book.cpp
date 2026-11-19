#include <sstream>

#include "book.h"

using namespace std;

//constructeur par defaut pour un livre vide qui est disponible
Book::Book() : title(""), author(""), isbn(""), isAvailable(true), borrowerId(""){}

//constructeur avec parametre : un nouveau livre est disponible
Book::Book(const string& title, const string& author, const string& isbn) {
    this -> title = title;
    this -> author = author;
    this -> isbn = isbn;
    this -> isAvailable = true;
    this -> borrowerId = "";
}

// GET
string Book::getTitle() const {return title;}
string Book::getAuthor() const {return author;}
string Book::getISBN() const {return isbn;}
bool Book::getAvailability() const {return isAvailable;}
string Book::getBorrowerId() const {return borrowerId;}

// set
void Book::setTitle(const string& title) {this->title = title;}
void Book::setAuthor(const string& author) {this->author = author;}
void Book::setISBN(const string& isbn) { this->isbn = isbn; }
void Book::setAvailability(bool available) {isAvailable = available;}
void Book::setBorrowerId(const string& id) {borrowerId = id;}

// Emprunter un livre
void Book::checkOut(const string& borrowerId){
    isAvailable = false;
    this->borrowerId = borrowerId;
}


//Retour d'un livre
void Book::returnBook(){
    isAvailable = true;
    borrowerId.clear();
}

// Affichage lisible
string Book::toString() const {
    string result = "Titre: " + title + "\nAuteur: " + author + "\nISBN: " + isbn +
                    "\nStatut: " + (isAvailable ? "Disponible" : "Emprunté");
    if (!isAvailable && !borrowerId.empty()) {
        result += " (par " + borrowerId + ")";
    }
    return result;
}
// Format du fichier titre|auteur|isbn|disponibilite(0/1)|idEmprunteur
string Book::toFileFormat() const{
    return title+"|"+author+"|"+isbn+"|"+(isAvailable ? "1":"0")+"|"+borrowerId;
}

// Lecture d'une ligne du fichier
void Book::fromFileFormat(const string& line){
    
    // fichier sous windows terminent par \r\n
    string clean = line;
    if(!clean.empty() && clean.back()=='\r'){
        clean.pop_back();
    }

    // coupe string clean quand on trouve |
    stringstream ss (clean);
    string availStr;

    getline(ss, title, '|');
    getline(ss, author, '|');
    getline(ss, isbn, '|');
    getline(ss, availStr, '|');
    getline(ss, borrowerId, '|');

    isAvailable = (availStr != "0");
}