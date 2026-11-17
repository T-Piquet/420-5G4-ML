"""Fenêtre principale et navigation entre les pages."""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from pages import AddBookPage, AddUserPage, BookDetailPage, HomePage, UsersPage
from statistics_modal import StatisticsModal


class MainWindow(QMainWindow):
    """Routeur minimal basé sur un QStackedWidget."""

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._statistics_modal = None

        self.setWindowTitle("Système de Gestion de Bibliothèque Personnelle")
        self.resize(1240, 820)
        self.setMinimumSize(980, 680)

        self.home_page = HomePage(service)
        self.book_page = BookDetailPage(service)
        self.users_page = UsersPage(service)
        self.add_book_page = AddBookPage(service)
        self.add_user_page = AddUserPage(service)

        self.stack = QStackedWidget()
        self.stack.setObjectName("Stack")
        for page in (
            self.home_page,
            self.book_page,
            self.users_page,
            self.add_book_page,
            self.add_user_page,
        ):
            self.stack.addWidget(page)

        root = QWidget()
        root.setObjectName("Root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.setCentralWidget(root)

        # Navigation depuis l'accueil.
        self.home_page.book_activated.connect(self.show_book)
        self.home_page.users_requested.connect(self.show_users)
        self.home_page.statistics_requested.connect(self.show_statistics)
        self.home_page.add_book_requested.connect(self.show_add_book)

        # Page de détail.
        self.book_page.back_requested.connect(self.show_home)

        # Page des utilisateurs.
        self.users_page.back_requested.connect(self.show_home)
        self.users_page.add_user_requested.connect(self.show_add_user)

        # Création d'un livre.
        self.add_book_page.back_requested.connect(self.show_home)
        self.add_book_page.added.connect(self.show_home)

        # Création d'un utilisateur.
        self.add_user_page.back_requested.connect(self.show_users)
        self.add_user_page.added.connect(self.show_users)

        self.show_home()

    def show_home(self) -> None:
        self.home_page.reload()
        self.stack.setCurrentWidget(self.home_page)

    def show_book(self, isbn: str) -> None:
        if self.book_page.load(isbn):
            self.stack.setCurrentWidget(self.book_page)

    def show_users(self) -> None:
        self.users_page.reload()
        self.stack.setCurrentWidget(self.users_page)

    def show_add_book(self) -> None:
        self.add_book_page.reset()
        self.stack.setCurrentWidget(self.add_book_page)

    def show_add_user(self) -> None:
        self.add_user_page.reset()
        self.stack.setCurrentWidget(self.add_user_page)

    def show_statistics(self) -> None:
        """Page 8 : la modale s'ouvre par-dessus la page 1, qui reste visible."""
        if self._statistics_modal is not None:
            return

        self._statistics_modal = StatisticsModal(
            self._service.statistics(), self.centralWidget()
        )
        self._statistics_modal.closed.connect(self._close_statistics)

        # La pile est désactivée : la modale est seule à recevoir les clics.
        self.stack.setEnabled(False)
        self._statistics_modal.show()
        self._statistics_modal.raise_()
        self._statistics_modal.setFocus()

    def _close_statistics(self) -> None:
        modal = self._statistics_modal

        if modal is None:
            return

        self._statistics_modal = None
        self.stack.setEnabled(True)
        self.home_page.statistics_button.setFocus()
        modal.deleteLater()

    def closeEvent(self, event) -> None:
        self._service.save()
        super().closeEvent(event)
