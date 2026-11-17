"""Page 8 : fenêtre modale des statistiques, au-dessus de l'accueil assombri."""

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from theme import BLUE, GREEN, RED
from widgets import primary_button

CARD_WIDTH = 540


def _stat_card(value: int, label: str, accent_color: str) -> QFrame:
    """Carte blanche avec un liseré de couleur, un grand chiffre et son libellé."""
    card = QFrame()
    card.setObjectName("StatCard")
    card.setMinimumHeight(88)

    accent = QFrame()
    accent.setFixedWidth(5)
    accent.setStyleSheet(
        f"background-color: {accent_color};"
        "border-top-left-radius: 12px;"
        "border-bottom-left-radius: 12px;"
    )

    value_label = QLabel(str(value))
    value_label.setObjectName("StatisticsValue")

    text_label = QLabel(label)
    text_label.setObjectName("StatisticsLabel")

    content = QVBoxLayout()
    content.setContentsMargins(16, 10, 16, 10)
    content.setSpacing(2)
    content.addWidget(value_label)
    content.addWidget(text_label)
    content.addStretch(1)

    root = QHBoxLayout(card)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)
    root.addWidget(accent)
    root.addLayout(content, 1)

    return card


class StatisticsModal(QWidget):
    """Page 8 : statistiques affichées par-dessus la page 1, sans changer de page."""

    closed = pyqtSignal()

    def __init__(self, statistics, parent):
        super().__init__(parent)
        self._parent = parent
        self._closing = False

        self.setObjectName("StatisticsOverlay")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setGeometry(parent.rect())

        self.card = QFrame()
        self.card.setObjectName("StatisticsCard")
        self.card.setFixedWidth(CARD_WIDTH)

        title = QLabel("Statistiques")
        title.setObjectName("StatisticsTitle")

        close_button = QPushButton("×")
        close_button.setObjectName("DialogCloseButton")
        close_button.setToolTip("Fermer")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self._close)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(close_button, 0, Qt.AlignTop)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for column in range(2):
            grid.setColumnStretch(column, 1)

        cards = (
            (statistics.users, "Utilisateurs", BLUE),
            (statistics.books, "Livres", BLUE),
            (statistics.available, "Livres disponibles", GREEN),
            (statistics.borrowed, "Livres empruntés", RED),
        )
        for index, (value, label, color) in enumerate(cards):
            grid.addWidget(_stat_card(value, label, color), index // 2, index % 2)

        self.close_button = primary_button("Fermer")
        self.close_button.clicked.connect(self._close)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(26, 22, 26, 24)
        card_layout.setSpacing(18)
        card_layout.addLayout(title_row)
        card_layout.addLayout(grid)
        card_layout.addWidget(self.close_button)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.card)
        row.addStretch(1)
        root.addLayout(row)
        root.addStretch(1)

        parent.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self._parent and event.type() == QEvent.Resize:
            self.setGeometry(self._parent.rect())
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        # Un clic en dehors de la carte ferme la modale, comme dans la maquette.
        if event.button() == Qt.LeftButton and not self.card.geometry().contains(
            event.pos()
        ):
            self._close()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._close()
            return
        super().keyPressEvent(event)

    def _close(self) -> None:
        if self._closing:
            return

        self._closing = True
        self.closed.emit()
