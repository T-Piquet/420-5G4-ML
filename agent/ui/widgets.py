"""Composants réutilisables : cartes de livre, cartes d'utilisateur, champs."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from theme import GREEN, RED, TEXT_MUTED


def set_placeholder_color(line_edit: QLineEdit, color: str = TEXT_MUTED) -> None:
    """Qt ne gère pas la couleur du placeholder en QSS : on passe par la palette."""
    palette = line_edit.palette()
    palette.setColor(QPalette.PlaceholderText, QColor(color))
    line_edit.setPalette(palette)


def create_input(placeholder: str, min_height: int = 0) -> QLineEdit:
    field = QLineEdit()
    field.setPlaceholderText(placeholder)
    set_placeholder_color(field)
    if min_height:
        field.setMinimumHeight(min_height)
    return field


def primary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setCursor(Qt.PointingHandCursor)
    return button


class BookCard(QFrame):
    """Carte cliquable représentant un livre."""

    activated = pyqtSignal(str)

    def __init__(self, book, parent=None):
        super().__init__(parent)
        self._isbn = book.isbn
        self.setObjectName("BookCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(98)

        accent = QFrame()
        accent.setFixedWidth(6)
        accent_color = GREEN if book.available else RED
        accent.setStyleSheet(
            f"background-color: {accent_color};"
            "border-top-left-radius: 12px;"
            "border-bottom-left-radius: 12px;"
        )

        title = QLabel(book.title)
        title.setObjectName("CardTitle")

        author = QLabel(book.author)
        author.setObjectName("CardMeta")

        isbn = QLabel(book.isbn)
        isbn.setObjectName("CardMeta")

        left = QVBoxLayout()
        left.setSpacing(3)
        left.addWidget(title)
        left.addWidget(author)
        left.addWidget(isbn)
        left.addStretch(1)

        status = QLabel("Non emprunté" if book.available else "Emprunté")
        status.setObjectName("StatusAvailable" if book.available else "StatusBorrowed")
        status.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self._borrower = QLabel("")
        self._borrower.setObjectName("BorrowerName")
        self._borrower.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        right = QVBoxLayout()
        right.setSpacing(3)
        right.addWidget(status)
        right.addWidget(self._borrower)
        right.addStretch(1)

        content = QHBoxLayout()
        content.setContentsMargins(16, 12, 16, 12)
        content.setSpacing(10)
        content.addLayout(left, 1)
        content.addLayout(right, 0)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(accent)
        root.addLayout(content, 1)

    def set_borrower_name(self, name: str) -> None:
        self._borrower.setText(name)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.activated.emit(self._isbn)
        super().mouseReleaseEvent(event)


class UserCard(QFrame):
    """Carte non cliquable représentant un utilisateur."""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setObjectName("UserCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(78)
        self.setMaximumHeight(88)

        name = QLabel(user.name)
        name.setObjectName("UserCardName")
        name.setAlignment(Qt.AlignCenter)

        user_id = QLabel(f"N° {user.user_id}")
        user_id.setObjectName("UserCardId")
        user_id.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        layout.addWidget(name)
        layout.addWidget(user_id)
