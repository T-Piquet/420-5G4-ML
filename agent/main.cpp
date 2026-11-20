#include <iostream>
#include <limits>
#include <string>
#include <filesystem>

#include "library.h"
#include "filemanager.h"
#include "console_color.h"

using namespace std;

void clearScreen() {
    system("cls || clear");
}

void pauseForInput() {
    cout << "\n" << Color::dim() << "Appuyez sur Entrée pour continuer..." << Color::reset();
    cin.ignore();
    cin.get();
}

void displayMenu() {
    cout << "\n" << Color::bold_cyan() << "=== SYSTÈME DE GESTION DE BIBLIOTHÈQUE PERSONNELLE ===" << Color::reset() << "\n";
    cout << Color::cyan() << "1."  << Color::reset() << "  Ajouter un Livre\n";
    cout << Color::cyan() << "2."  << Color::reset() << "  Supprimer un Livre\n";
    cout << Color::cyan() << "3."  << Color::reset() << "  Rechercher des Livres par Titre\n";
    cout << Color::cyan() << "4."  << Color::reset() << "  Rechercher des Livres par Auteur\n";
    cout << Color::cyan() << "5."  << Color::reset() << "  Afficher Tous les Livres\n";
    cout << Color::cyan() << "6."  << Color::reset() << "  Afficher les Livres Disponibles\n";
    cout << Color::cyan() << "7."  << Color::reset() << "  Ajouter un Utilisateur\n";
    cout << Color::cyan() << "8."  << Color::reset() << "  Afficher Tous les Utilisateurs\n";
    cout << Color::cyan() << "9."  << Color::reset() << "  Emprunter un Livre\n";
    cout << Color::cyan() << "10." << Color::reset() << " Retourner un Livre\n";
    cout << Color::cyan() << "11." << Color::reset() << " Statistiques de la Bibliothèque\n";
    cout << Color::cyan() << "12." << Color::reset() << " Sauvegarder les Données\n";
    cout << Color::cyan() << "13." << Color::reset() << " Créer une Sauvegarde\n";
    cout << Color::cyan() << "0."  << Color::reset() << "  Quitter\n";
    cout << Color::bold_cyan() << "=======================================================" << Color::reset() << "\n";
    cout << Color::bold() << "Entrez votre choix : " << Color::reset();
}

string getInput(const string& prompt) {
    string input;
    cout << prompt;
    getline(cin, input);
    return input;
}

void printUsage(const char* programName) {
    cerr << "Usage: " << programName << " [--data-dir|-d <répertoire>]\n";
}

int main(int argc, char* argv[]) {
    string dataDir;

    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--data-dir" || arg == "-d") {
            if (i + 1 >= argc) {
                cerr << "Erreur : " << arg << " nécessite un répertoire.\n";
                printUsage(argv[0]);
                return 1;
            }
            dataDir = argv[++i];
        } else {
            cerr << "Erreur : argument inconnu '" << arg << "'.\n";
            printUsage(argv[0]);
            return 1;
        }
    }

    string booksFile;
    string usersFile;
    if (!dataDir.empty()) {
        if (!filesystem::is_directory(dataDir)) {
            cerr << "Erreur : le répertoire " << dataDir << " n'existe pas.\n";
            printUsage(argv[0]);
            return 1;
        }
        booksFile = (filesystem::path(dataDir) / "books.txt").string();
        usersFile = (filesystem::path(dataDir) / "users.txt").string();
    }

    Library library;
    FileManager fileManager(booksFile, usersFile);
    
    // Load existing data
    cout << Color::cyan() << "Chargement des données de la bibliothèque..." << Color::reset() << "\n";
    fileManager.loadLibraryData(library);
    
    int choice;
    bool running = true;
    
    while (running) {
        displayMenu();
        
        if (!(cin >> choice)) {
            cout << Color::bold_red() << "Saisie invalide. Veuillez entrer un nombre." << Color::reset() << "\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            pauseForInput();
            continue;
        }
        cin.ignore(); // Clear newline from buffer
        
        switch (choice) {
            case 1: { // Add Book
                string title = getInput("Entrez le titre du livre : ");
                string author = getInput("Entrez l'auteur du livre : ");
                string isbn = getInput("Entrez l'ISBN du livre : ");
                
                if (library.findBookByISBN(isbn)) {
                    cout << Color::bold_red() << "Erreur : Un livre avec l'ISBN " << isbn << " existe déjà." << Color::reset() << "\n";
                } else {
                    Book newBook(title, author, isbn);
                    library.addBook(newBook);
                    cout << Color::green() << "Livre ajouté avec succès !" << Color::reset() << "\n";
                }
                pauseForInput();
                break;
            }
            
            case 2: { // Remove Book
                string isbn = getInput("Entrez l'ISBN du livre à supprimer : ");
                
                if (library.removeBook(isbn)) {
                    cout << Color::green() << "Livre supprimé avec succès !" << Color::reset() << "\n";
                } else {
                    cout << Color::bold_red() << "Livre non trouvé." << Color::reset() << "\n";
                }
                pauseForInput();
                break;
            }
            
            case 3: { // Search by Title
                string title = getInput("Entrez le titre à rechercher : ");
                auto results = library.searchBooksByTitle(title);
                
                if (results.empty()) {
                    cout << Color::yellow() << "Aucun livre trouvé avec ce titre." << Color::reset() << "\n";
                } else {
                    cout << "\n" << Color::bold_cyan() << "=== RÉSULTATS DE RECHERCHE ===" << Color::reset() << "\n";
                    for (size_t i = 0; i < results.size(); ++i) {
                        cout << "\n" << Color::cyan() << "Résultat " << (i + 1) << " :" << Color::reset() << "\n";
                        cout << results[i]->toString() << "\n";
                        cout << Color::dim() << "-----------------------------" << Color::reset() << "\n";
                    }
                }
                pauseForInput();
                break;
            }
            
            case 4: { // Search by Author
                string author = getInput("Entrez l'auteur à rechercher : ");
                auto results = library.searchBooksByAuthor(author);
                
                if (results.empty()) {
                    cout << Color::yellow() << "Aucun livre trouvé de cet auteur." << Color::reset() << "\n";
                } else {
                    cout << "\n" << Color::bold_cyan() << "=== RÉSULTATS DE RECHERCHE ===" << Color::reset() << "\n";
                    for (size_t i = 0; i < results.size(); ++i) {
                        cout << "\n" << Color::cyan() << "Résultat " << (i + 1) << " :" << Color::reset() << "\n";
                        cout << results[i]->toString() << "\n";
                        cout << Color::dim() << "-----------------------------" << Color::reset() << "\n";
                    }
                }
                pauseForInput();
                break;
            }
            
            case 5: // Display All Books
                library.displayAllBooks();
                pauseForInput();
                break;
            
            case 6: // Display Available Books
                library.displayAvailableBooks();
                pauseForInput();
                break;
            
            case 7: { // Add User
                string name = getInput("Entrez le nom de l'utilisateur : ");
                string userId = getInput("Entrez l'ID de l'utilisateur : ");
                
                if (library.findUserById(userId)) {
                    cout << Color::bold_red() << "Erreur : Un utilisateur avec l'ID " << userId << " existe déjà." << Color::reset() << "\n";
                } else {
                    User newUser(name, userId);
                    library.addUser(newUser);
                    cout << Color::green() << "Utilisateur ajouté avec succès !" << Color::reset() << "\n";
                }
                pauseForInput();
                break;
            }
            
            case 8: // Display All Users
                library.displayAllUsers();
                pauseForInput();
                break;
            
            case 9: { // Check Out Book
                string isbn = getInput("Entrez l'ISBN du livre à emprunter : ");
                string userId = getInput("Entrez l'ID de l'utilisateur : ");
                
                if (library.checkOutBook(isbn, userId)) {
                    cout << Color::green() << "Livre emprunté avec succès !" << Color::reset() << "\n";
                } else {
                    cout << Color::bold_red() << "Erreur : Impossible d'emprunter le livre. Vérifiez l'ISBN, l'ID utilisateur et la disponibilité du livre." << Color::reset() << "\n";
                }
                pauseForInput();
                break;
            }
            
            case 10: { // Return Book
                string isbn = getInput("Entrez l'ISBN du livre à retourner : ");
                
                if (library.returnBook(isbn)) {
                    cout << Color::green() << "Livre retourné avec succès !" << Color::reset() << "\n";
                } else {
                    cout << Color::bold_red() << "Erreur : Impossible de retourner le livre. Vérifiez l'ISBN et que le livre est bien emprunté." << Color::reset() << "\n";
                }
                pauseForInput();
                break;
            }
            
            case 11: { // Library Statistics
                cout << "\n" << Color::bold_cyan() << "=== STATISTIQUES DE LA BIBLIOTHÈQUE ===" << Color::reset() << "\n";
                cout << "Total des Livres : " << Color::bold() << library.getTotalBooks() << Color::reset() << "\n";
                cout << "Livres Disponibles : " << Color::green() << library.getAvailableBookCount() << Color::reset() << "\n";
                cout << "Livres Empruntés : " << Color::yellow() << library.getCheckedOutBookCount() << Color::reset() << "\n";
                cout << "Total des Utilisateurs : " << Color::bold() << library.getAllUsers().size() << Color::reset() << "\n";
                pauseForInput();
                break;
            }
            
            case 12: { // Save Data
                if (fileManager.saveLibraryData(library)) {
                    cout << Color::green() << "Données de la bibliothèque sauvegardées avec succès !" << Color::reset() << "\n";
                } else {
                    cout << Color::bold_red() << "Erreur lors de la sauvegarde des données de la bibliothèque." << Color::reset() << "\n";
                }
                pauseForInput();
                break;
            }
            
            case 13: { // Create Backup
                fileManager.createBackup();
                pauseForInput();
                break;
            }
            
            case 0: // Exit
                cout << Color::cyan() << "Sauvegarde des données avant la fermeture..." << Color::reset() << "\n";
                fileManager.saveLibraryData(library);
                cout << Color::bold_cyan() << "Merci d'avoir utilisé le Système de Gestion de Bibliothèque Personnelle !" << Color::reset() << "\n";
                running = false;
                break;
            
            default:
                cout << Color::bold_red() << "Choix invalide. Veuillez réessayer." << Color::reset() << "\n";
                pauseForInput();
                break;
        }
    }
    
    return 0;
}