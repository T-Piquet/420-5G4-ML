"""Palette de couleurs et feuille de style de l'interface."""

from string import Template

NAVY = "#0F1A2B"
NAVY_SOFT = "#1B2A40"
SURFACE = "#F4F6FA"
CARD = "#FFFFFF"
USER_CARD = "#E9EDF5"
BLUE = "#2563EB"
BLUE_DARK = "#1D4ED8"
TEXT = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
TEXT_DARK = "#0F172A"
TEXT_DARK_MUTED = "#64748B"
RED = "#EF4444"
GREEN = "#10B981"
FIELD = "#1F2A3C"
FIELD_BORDER = "#2C3A52"

_QSS = Template(
    """
QWidget {
    font-family: "Inter", "Segoe UI", "DejaVu Sans", sans-serif;
    font-size: 14px;
    color: $text;
}

QMainWindow, QWidget#Root, QStackedWidget#Stack {
    background-color: $navy;
}

QLabel {
    background: transparent;
}

QPushButton {
    border: none;
    border-radius: 18px;
    padding: 9px 22px;
    min-height: 22px;
    font-weight: 600;
    color: #FFFFFF;
    background-color: $blue;
}
QPushButton:hover {
    background-color: $blue_dark;
}
QPushButton:pressed {
    background-color: #1E40AF;
}
QPushButton:disabled {
    background-color: #334155;
    color: #94A3B8;
}

QPushButton#FilterButton {
    background-color: $navy_soft;
    color: $text;
    border: 1px solid $field_border;
}
QPushButton#FilterButton:hover {
    background-color: #22334D;
}

QLineEdit {
    background-color: $field;
    border: 1px solid $field_border;
    border-radius: 10px;
    padding: 12px 14px;
    color: $text;
    selection-background-color: $blue;
}
QLineEdit:focus {
    border: 1px solid $blue;
}

QFrame#BookCard {
    background-color: $card;
    border-radius: 12px;
}
QFrame#BookCard:hover {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
}

QFrame#UserCard {
    background-color: $user_card;
    border-radius: 12px;
}

QFrame#Panel {
    background-color: $surface;
    border-radius: 16px;
    color: $text_dark;
}

QLabel#DetailTitle {
    font-size: 30px;
    font-weight: 700;
    color: $text_dark;
}
QLabel#DetailAuthor {
    font-size: 16px;
    color: $text_dark_muted;
}
QLabel#DetailStatusBorrowed {
    font-size: 17px;
    font-weight: 700;
    color: $red;
}
QLabel#DetailStatusAvailable {
    font-size: 17px;
    font-weight: 700;
    color: $green;
}
QLabel#DetailText {
    font-size: 15px;
    color: $text_dark;
}

QLabel#CardTitle {
    font-size: 15px;
    font-weight: 700;
    color: $text_dark;
}
QLabel#CardMeta {
    font-size: 12px;
    color: $text_dark_muted;
}
QLabel#StatusBorrowed {
    font-size: 13px;
    font-weight: 600;
    color: $red;
}
QLabel#StatusAvailable {
    font-size: 13px;
    font-weight: 600;
    color: $green;
}
QLabel#BorrowerName {
    font-size: 13px;
    color: $text_dark_muted;
}

QLabel#UserCardName {
    font-size: 15px;
    font-weight: 700;
    color: $text_dark;
}
QLabel#UserCardId {
    font-size: 13px;
    color: $text_dark_muted;
}

QLabel#ErrorLabel {
    font-size: 13px;
    color: $red;
}
QLabel#EmptyLabel {
    font-size: 15px;
    color: $text_muted;
}

QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QMenu {
    background-color: $navy_soft;
    border: 1px solid $field_border;
    border-radius: 10px;
    padding: 6px;
    color: $text;
}
QMenu::item {
    padding: 9px 26px 9px 14px;
    border-radius: 6px;
}
QMenu::item:selected {
    background-color: $blue;
}

QWidget#StatisticsOverlay {
    background-color: rgba(10, 18, 32, 190);
}

QFrame#StatisticsCard {
    background-color: $surface;
    border-radius: 18px;
}
QLabel#StatisticsTitle {
    font-size: 26px;
    font-weight: 700;
    color: $text_dark;
}
QFrame#StatCard {
    background-color: $card;
    border-radius: 12px;
}
QLabel#StatisticsValue {
    font-size: 32px;
    font-weight: 700;
    color: $text_dark;
}
QLabel#StatisticsLabel {
    font-size: 14px;
    color: $text_dark_muted;
}

QPushButton#StatisticsButton {
    background-color: $navy_soft;
    color: $text;
    border: 1px solid $field_border;
}
QPushButton#StatisticsButton:hover {
    background-color: #22334D;
}

QPushButton#DialogCloseButton {
    background: transparent;
    color: $text_dark_muted;
    font-size: 18px;
    font-weight: 600;
    border-radius: 15px;
    min-height: 30px;
    max-height: 30px;
    min-width: 30px;
    max-width: 30px;
    padding: 0;
}
QPushButton#DialogCloseButton:hover {
    background-color: #E2E8F0;
    color: $text_dark;
}
"""
)

STYLESHEET = _QSS.substitute(
    navy=NAVY,
    navy_soft=NAVY_SOFT,
    surface=SURFACE,
    card=CARD,
    user_card=USER_CARD,
    blue=BLUE,
    blue_dark=BLUE_DARK,
    text=TEXT,
    text_muted=TEXT_MUTED,
    text_dark=TEXT_DARK,
    text_dark_muted=TEXT_DARK_MUTED,
    red=RED,
    green=GREEN,
    field=FIELD,
    field_border=FIELD_BORDER,
)
