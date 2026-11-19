Plan ajusté — interface Tkinter « menu texte », données agent/data par défaut + choix
1. Environnement à prévoir
- tkinter n’est pas installé pour /usr/bin/python3 ici, mais DISPLAY=:0 est présent et le X11 forwarding fonctionne via VS Code.
- Le devcontainer suivi agent/.devcontainer/Dockerfile:17-20 installe python3-tk ; le .devcontainer/ racine, minimal et non suivi, ne l’installe pas. Prévoir apt-get install -y python3-tk si vous travaillez depuis la racine.
- pybind11 n’est pas installé non plus. Prévoir python3 -m pip install pybind11 avec le même interpréteur que celui qui lance l’interface.
2. Côté C++ : façade + bindings
Ne pas binder main.cpp : il contient seulement le menu, les prompts et les cout. Ajouter agent/session.h / session.cpp avec une classe LibrarySession qui possède Library + FileManager, puis binder cette façade.
API à exposer :
LibrarySession(const std::string& data_dir);   // chemin absolu recommandé

bool reload();
bool add_book(title, author, isbn);
bool remove_book(isbn);
std::vector<Book> search_books_by_title(text) const;
std::vector<Book> search_books_by_author(text) const;
std::vector<Book> get_all_books() const;
std::vector<Book> get_available_books() const;
bool add_user(name, user_id);
std::vector<User> get_all_users() const;
bool check_out_book(isbn, user_id);
bool return_book(isbn);
std::map<std::string, int> stats() const;      // total_books, available_books, checked_out_books, total_users
bool save();
bool backup();
Binder aussi Book et User comme objets de données en lecture seule :
- Book : title, author, isbn, available, borrower_id ;
- User : name, user_id, borrowed_books.
Ne pas exposer toFileFormat/fromFileFormat, display..., ni les mutations bas niveau Book::checkOut, User::borrowBook, etc. Retourner des copies de Book/User pour éviter les pointeurs pendants côté Python.
Pièges à traiter dans la façade :
- contrôles de doublon ISBN/ID actuellement dans main.cpp:111-117 et main.cpp:184-190 ;
- FileManager::loadLibraryData() ajoute aux données existantes (filemanager.cpp:18-22) → reload() doit repartir d’un Library neuf ;
- createBackup() peut lever si le .backup existe (filemanager.cpp:112-123) → retourner false ;
- removeBook() ne nettoie pas les emprunts utilisateurs (library.cpp:17-28) → appeler returnBook(isbn) avant suppression ;
- retirer les cout de FileManager ou les remplacer par des statuts, sinon les messages n’apparaîtront pas dans la GUI.
3. CMake / module Python
Restructurer agent/CMakeLists.txt :
- bibliotheque_core : book.cpp, user.cpp, library.cpp, filemanager.cpp, session.cpp ;
- bibliotheque : main.cpp + bibliotheque_core ;
- bibliotheque_py : bindings.cpp + bibliotheque_core, créé avec pybind11_add_module(...).
Le file(GLOB "*.cpp") actuel inclurait main.cpp dans le module Python ; à éviter.
4. Interface Tkinter (agent/interface_tk.py)
Structure d’écran :
- ttk.Listbox à gauche avec les 14 entrées 0 à 13, libellés identiques à main.cpp:21-39 ;
- scrolledtext.ScrolledText à droite servant de « console » : menu, prompts et résultats en français ;
- en bas : ttk.Entry pour le numéro de choix + bouton Exécuter ; Entrée et double-clic dans la Listbox déclenchent aussi l’action ;
- un cadre Paramètres dynamique avec des ttk.Entry selon le choix, plutôt que des popups modal ;
- bouton Choisir un dossier… (filedialog.askdirectory) et ttk.Label affichant le dossier courant, agent/data par défaut résolu via Path(__file__).resolve().parent / "data" ;
- bouton Sauvegarder optionnel en plus du choix 12.
Champs dynamiques :
Choix
1 Ajouter un livre
2 Supprimer un livre
3 Recherche par titre
4 Recherche par auteur
5 / 6 / 8 / 11 / 12 / 13
7 Ajouter un utilisateur
9 Emprunter
10 Retourner
0 Quitter
Comportement :
- écrire dans la zone de texte les mêmes messages français que main.cpp:105-262 (succès/erreur), avec ScrolledText passé en normal puis disabled après insertion ;
- formater les livres/utilisateurs depuis les propriétés Python, pas depuis toString() (fautes de frappe et format console) ;
- pour les statistiques, reprendre exactement les 4 lignes de main.cpp:225-231 ;
- sur changement de dossier : recréer/reloader LibrarySession et vider la console ;
- sur fermeture de fenêtre (WM_DELETE_WINDOW) : appeler save() comme le choix 0.
5. Build et lancement
python3 -m pip install pybind11
sudo apt-get install -y python3-tk
cmake -S agent -B agent/build -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)"
cmake --build agent/build
PYTHONPATH=agent/build python3 agent/interface_tk.py
6. Vérification
- Compiler bibliotheque et vérifier que le CLI d’origine fonctionne toujours.
- Test Python sans GUI sur une copie temporaire de agent/data/ : ajout, recherche, emprunt, retour, stats, sauvegarde, backup.
- Test GUI : lancement avec agent/data, chaque choix 0-13, changement de dossier, fermeture avec sauvegarde.
- Ne jamais sauvegarder directement dans le agent/data/ suivi pendant les tests.