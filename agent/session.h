#ifndef SESSION_H
#define SESSION_H

#include <map>
#include <memory>
#include <string>
#include <vector>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

using namespace std;

class LibrarySession {
private:
    unique_ptr<Library> library;
    FileManager fileManager;
    vector<string> messages;

public:
    explicit LibrarySession(const string& data_dir);

    bool reload();

    bool add_book(const string& title, const string& author, const string& isbn);
    bool remove_book(const string& isbn);
    vector<Book> search_books_by_title(const string& text) const;
    vector<Book> search_books_by_author(const string& text) const;
    vector<Book> get_all_books() const;
    vector<Book> get_available_books() const;

    bool add_user(const string& name, const string& user_id);
    vector<User> get_all_users() const;

    bool check_out_book(const string& isbn, const string& user_id);
    bool return_book(const string& isbn);

    map<string, int> stats() const;

    bool save();
    bool backup();

    const vector<string>& get_messages() const;
    void clear_messages();
};

#endif
