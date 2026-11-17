"""Pages de l'application, conformes aux maquettes `maquette/AiReview`."""

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from widgets import BookCard, UserCard, create_input, primary_button

COLUMNS = 3


def _clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            # setParent(None) retire immédiatement le widget de l'affichage ;
            # deleteLater() libère la mémoire au prochain tour de boucle.
            widget.setParent(None)
            widget.deleteLater()


def _make_panel() -> tuple:
    panel = QFrame()
    panel.setObjectName("Panel")

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(30, 26, 30, 26)
    layout.setSpacing(14)

    return panel, layout


def _make_scroll_grid():
    host = QWidget()
    host_layout = QVBoxLayout(host)
    host_layout.setContentsMargins(0, 0, 0, 0)
    host_layout.setSpacing(0)

    grid = QGridLayout()
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(16)
    grid.setVerticalSpacing(16)
    for column in range(COLUMNS):
        grid.setColumnStretch(column, 1)

    host_layout.addLayout(grid)
    host_layout.addStretch(1)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(host)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    return scroll, grid


def _empty_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("EmptyLabel")
    label.setAlignment(Qt.AlignCenter)
    return label


class HomePage(QWidget):
    """Page 1 (et page 2) : accueil, liste des livres."""

    book_activated = pyqtSignal(str)
    users_requested = pyqtSignal()
    statistics_requested = pyqtSignal()
    add_book_requested = pyqtSignal()

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._status_filter = "all"

        self.users_button = primary_button("Utilisateur →")
        self.statistics_button = primary_button("Statistiques")
        self.statistics_button.setObjectName("StatisticsButton")
        self.add_button = primary_button("Ajouter un livre")

        self.search = create_input("Recherche : titre ou auteur")

        self.filter_button = QPushButton("Filtre")
        self.filter_button.setObjectName("FilterButton")
        self.filter_button.setFixedWidth(150)
        self.filter_button.setCursor(Qt.PointingHandCursor)

        self.filter_menu = QMenu(self)
        group = QActionGroup(self.filter_menu)
        group.setExclusive(True)

        for key, label in (
            ("all", "Aucun"),
            ("borrowed", "Emprunté"),
            ("available", "Non emprunté"),
        ):
            action = QAction(label, self.filter_menu)
            action.setCheckable(True)
            action.setData(key)
            action.setChecked(key == "all")
            group.addAction(action)
            self.filter_menu.addAction(action)

        self.filter_menu.triggered.connect(self._on_filter_selected)

        # Trois colonnes de même largeur : « Statistiques » reste centré.
        header = QGridLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.users_button, 0, 0, Qt.AlignLeft)
        header.addWidget(self.statistics_button, 0, 1, Qt.AlignCenter)
        header.addWidget(self.add_button, 0, 2, Qt.AlignRight)
        for column in range(3):
            header.setColumnStretch(column, 1)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(self.filter_button)

        self.scroll, self.grid = _make_scroll_grid()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(16)
        root.addLayout(header)
        root.addLayout(search_row)
        root.addWidget(self.scroll, 1)

        self.search.textChanged.connect(self.refresh)
        self.filter_button.clicked.connect(self._show_filter_menu)
        self.users_button.clicked.connect(self.users_requested)
        self.statistics_button.clicked.connect(self.statistics_requested)
        self.add_button.clicked.connect(self.add_book_requested)

    def _show_filter_menu(self) -> None:
        position = self.filter_button.mapToGlobal(
            QPoint(0, self.filter_button.height() + 6)
        )
        self.filter_menu.exec_(position)

    def _on_filter_selected(self, action) -> None:
        self._status_filter = action.data()
        self.refresh()

    def reload(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        _clear_layout(self.grid)

        query = self.search.text().strip().casefold()
        books = []

        for book in self._service.books():
            if query and query not in book.title.casefold() and query not in book.author.casefold():
                continue
            if self._status_filter == "borrowed" and book.available:
                continue
            if self._status_filter == "available" and not book.available:
                continue
            books.append(book)

        if not books:
            self.grid.addWidget(
                _empty_label("Aucun livre ne correspond à cet affichage."),
                0, 0, 1, COLUMNS,
            )
            return

        for index, book in enumerate(books):
            card = BookCard(book)

            if not book.available:
                borrower = self._service.find_user_by_id(book.borrower_id)
                card.set_borrower_name(borrower.name if borrower else book.borrower_id)

            card.activated.connect(self.book_activated)
            self.grid.addWidget(card, index // COLUMNS, index % COLUMNS)


class BookDetailPage(QWidget):
    """Pages 3 et 4 : détail d'un livre emprunté ou non emprunté."""

    back_requested = pyqtSignal()

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._isbn = ""

        self.back_button = primary_button("← Retour")
        self.back_button.clicked.connect(self.back_requested)

        self.title = QLabel("")
        self.title.setObjectName("DetailTitle")
        self.title.setWordWrap(True)

        self.author = QLabel("")
        self.author.setObjectName("DetailAuthor")

        # Vue « emprunté » (page 3)
        self.status_borrowed = QLabel("Emprunté")
        self.status_borrowed.setObjectName("DetailStatusBorrowed")

        self.borrower_label = QLabel("")
        self.borrower_label.setObjectName("DetailText")

        self.return_button = primary_button("Rendre le livre")
        self.return_button.clicked.connect(self._return_book)

        self.borrowed_view = QWidget()
        borrowed_layout = QVBoxLayout(self.borrowed_view)
        borrowed_layout.setContentsMargins(0, 0, 0, 0)
        borrowed_layout.setSpacing(10)
        borrowed_layout.addWidget(self.status_borrowed)
        borrowed_layout.addWidget(self.borrower_label)
        borrowed_layout.addStretch(1)
        borrowed_layout.addWidget(self.return_button)

        # Vue « non emprunté » (page 4)
        self.status_available = QLabel("Non emprunté")
        self.status_available.setObjectName("DetailStatusAvailable")

        self.name_input = create_input(
            "Nom de la personne qui veut emprunter le livre", min_height=72
        )

        self.borrow_button = primary_button("Emprunter le livre")
        self.borrow_button.clicked.connect(self._borrow_book)

        self.available_view = QWidget()
        available_layout = QVBoxLayout(self.available_view)
        available_layout.setContentsMargins(0, 0, 0, 0)
        available_layout.setSpacing(14)
        available_layout.addWidget(self.status_available)
        available_layout.addWidget(self.name_input)
        available_layout.addWidget(self.borrow_button)
        available_layout.addStretch(1)

        self.error = QLabel("")
        self.error.setObjectName("ErrorLabel")
        self.error.setWordWrap(True)
        self.error.hide()

        panel, panel_layout = _make_panel()
        panel_layout.addWidget(self.title)
        panel_layout.addWidget(self.author)
        panel_layout.addWidget(self.error)
        panel_layout.addSpacing(16)
        panel_layout.addWidget(self.borrowed_view, 1)
        panel_layout.addWidget(self.available_view, 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(16)
        root.addWidget(self.back_button, 0, Qt.AlignLeft)
        root.addWidget(panel, 1)

    def load(self, isbn: str) -> bool:
        book = self._service.find_book(isbn)

        if book is None:
            return False

        self._isbn = isbn
        self.title.setText(book.title)
        self.author.setText(book.author)
        self.error.hide()

        if book.available:
            self.borrowed_view.hide()
            self.available_view.show()
            self.name_input.clear()
            self.name_input.setFocus()
        else:
            self.available_view.hide()
            self.borrowed_view.show()

            borrower = self._service.find_user_by_id(book.borrower_id)
            name = borrower.name if borrower else (book.borrower_id or "inconnu")
            self.borrower_label.setText(f"Par : {name}")

        return True

    def _show_error(self, message: str) -> None:
        self.error.setText(message)
        self.error.show()

    def _borrow_book(self) -> None:
        ok, message = self._service.checkout(self._isbn, self.name_input.text())

        if not ok:
            self._show_error(message)
            return

        # Le livre est maintenant emprunté : on affiche la page 3.
        self.load(self._isbn)

    def _return_book(self) -> None:
        ok, message = self._service.return_book(self._isbn)

        if not ok:
            self._show_error(message)
            return

        # Le livre est maintenant disponible : on affiche la page 4.
        self.load(self._isbn)


class UsersPage(QWidget):
    """Page 5 : liste des utilisateurs."""

    back_requested = pyqtSignal()
    add_user_requested = pyqtSignal()

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service

        self.back_button = primary_button("← livre")
        self.add_button = primary_button("Ajouter un utilisateur")

        header = QHBoxLayout()
        header.addWidget(self.back_button)
        header.addStretch(1)
        header.addWidget(self.add_button)

        self.scroll, self.grid = _make_scroll_grid()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(16)
        root.addLayout(header)
        root.addWidget(self.scroll, 1)

        self.back_button.clicked.connect(self.back_requested)
        self.add_button.clicked.connect(self.add_user_requested)

    def reload(self) -> None:
        _clear_layout(self.grid)

        users = self._service.users()

        if not users:
            self.grid.addWidget(
                _empty_label("Aucun utilisateur enregistré."),
                0, 0, 1, COLUMNS,
            )
            return

        for index, user in enumerate(users):
            self.grid.addWidget(UserCard(user), index // COLUMNS, index % COLUMNS)


class AddBookPage(QWidget):
    """Page 6 : création d'un livre."""

    back_requested = pyqtSignal()
    added = pyqtSignal()

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service

        self.back_button = primary_button("← Retour")
        self.back_button.clicked.connect(self.back_requested)

        title = QLabel("Création de livre")
        title.setObjectName("DetailTitle")

        self.title_input = create_input("Titre du livre", min_height=58)
        self.author_input = create_input("Nom de l'auteur", min_height=58)
        self.isbn_input = create_input("ISBN", min_height=58)

        self.error = QLabel("")
        self.error.setObjectName("ErrorLabel")
        self.error.setWordWrap(True)
        self.error.hide()

        self.add_button = primary_button("Ajouter un livre")
        self.add_button.clicked.connect(self._submit)

        panel, panel_layout = _make_panel()
        panel_layout.addWidget(title)
        panel_layout.addSpacing(8)
        panel_layout.addWidget(self.title_input)
        panel_layout.addWidget(self.author_input)
        panel_layout.addWidget(self.isbn_input)
        panel_layout.addWidget(self.error)
        panel_layout.addWidget(self.add_button)
        panel_layout.addStretch(1)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(16)
        root.addWidget(self.back_button, 0, Qt.AlignLeft)
        root.addWidget(panel, 1)

    def reset(self) -> None:
        self.title_input.clear()
        self.author_input.clear()
        self.isbn_input.clear()
        self.error.hide()
        self.title_input.setFocus()

    def _submit(self) -> None:
        ok, message = self._service.add_book(
            self.title_input.text(),
            self.author_input.text(),
            self.isbn_input.text(),
        )

        if not ok:
            self.error.setText(message)
            self.error.show()
            return

        self.reset()
        self.added.emit()


class AddUserPage(QWidget):
    """Page 7 : création d'un utilisateur."""

    back_requested = pyqtSignal()
    added = pyqtSignal()

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service

        self.back_button = primary_button("← Retour")
        self.back_button.clicked.connect(self.back_requested)

        title = QLabel("Création de l'utilisateur")
        title.setObjectName("DetailTitle")

        self.name_input = create_input("Nom de la personne", min_height=58)
        self.id_input = create_input("Numéro d'utilisateur", min_height=58)

        self.error = QLabel("")
        self.error.setObjectName("ErrorLabel")
        self.error.setWordWrap(True)
        self.error.hide()

        self.add_button = primary_button("Ajouter un utilisateur")
        self.add_button.clicked.connect(self._submit)

        panel, panel_layout = _make_panel()
        panel_layout.addWidget(title)
        panel_layout.addSpacing(8)
        panel_layout.addWidget(self.name_input)
        panel_layout.addWidget(self.id_input)
        panel_layout.addWidget(self.error)
        panel_layout.addWidget(self.add_button)
        panel_layout.addStretch(1)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(16)
        root.addWidget(self.back_button, 0, Qt.AlignLeft)
        root.addWidget(panel, 1)

    def reset(self) -> None:
        self.name_input.clear()
        self.id_input.clear()
        self.error.hide()
        self.name_input.setFocus()

    def _submit(self) -> None:
        ok, message = self._service.add_user(
            self.name_input.text(),
            self.id_input.text(),
        )

        if not ok:
            self.error.setText(message)
            self.error.show()
            return

        self.reset()
        self.added.emit()
