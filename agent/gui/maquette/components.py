"""Composants réutilisables : navigation, cartes, badges, toasts et modales."""

from __future__ import annotations

from datetime import datetime
from tkinter import StringVar
from typing import Callable

import customtkinter as ctk

from .models import Book, LibraryStore, User
from .theme import COLORS, FONTS, MOIS, SPACING


class Card(ctk.CTkFrame):
    """Carte blanche arrondie du thème bibliothèque."""

    def __init__(self, master, padding: int = SPACING["card_padding"], **kwargs):
        kwargs.setdefault("fg_color", COLORS["surface"])
        kwargs.setdefault("corner_radius", SPACING["radius"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(master, **kwargs)
        self.padding = padding


class StatCard(Card):
    """Carte de statistique avec libellé, valeur et indicateur coloré."""

    def __init__(self, master, label: str, value: str, hint: str,
                 symbol: str, accent: str, soft: str):
        super().__init__(master, height=140)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 0))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text=label, font=FONTS["stat_label"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=0, column=0, sticky="w")

        icon = ctk.CTkFrame(top, width=36, height=36, corner_radius=10,
                            fg_color=soft)
        icon.grid_propagate(False)
        icon.grid(row=0, column=1)
        ctk.CTkLabel(icon, text=symbol, font=FONTS["icon"],
                     text_color=accent).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self, text=value, font=FONTS["stat_value"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=1, column=0, sticky="w", padx=18, pady=(4, 0))

        ctk.CTkLabel(self, text=hint, font=FONTS["stat_hint"],
                     text_color=COLORS["text_soft"], anchor="w").grid(
            row=2, column=0, sticky="w", padx=18, pady=(0, 14))


class Badge(ctk.CTkFrame):
    """Petite étiquette colorée (disponible, emprunté, etc.)."""

    def __init__(self, master, text: str, fg_color: str, text_color: str):
        super().__init__(master, fg_color=fg_color, corner_radius=9)
        self.label = ctk.CTkLabel(self, text=text, font=FONTS["badge"],
                                  text_color=text_color, fg_color="transparent")
        self.label.grid(padx=10, pady=3)

    def set_text(self, text: str) -> None:
        self.label.configure(text=text)


class NavItem(ctk.CTkFrame):
    """Entrée de navigation personnalisée avec indicateur actif."""

    def __init__(self, master, key: str, label: str, symbol: str,
                 command: Callable[[str], None]):
        super().__init__(master, fg_color="transparent", corner_radius=10,
                         height=44)
        self.grid_propagate(False)
        self.grid_columnconfigure(2, weight=1)
        self.key = key
        self._command = command
        self._active = False

        self.indicator = ctk.CTkFrame(self, width=3, height=20, corner_radius=2,
                                      fg_color="transparent")
        self.indicator.grid(row=0, column=0, padx=(7, 0), pady=12, sticky="ns")

        self.icon = ctk.CTkLabel(self, text=symbol, width=26,
                                 font=FONTS["icon_small"],
                                 text_color=COLORS["sidebar_text"],
                                 cursor="hand2")
        self.icon.grid(row=0, column=1, padx=(10, 6))

        self.label = ctk.CTkLabel(self, text=label, font=FONTS["nav"],
                                  text_color=COLORS["sidebar_text"],
                                  anchor="w", cursor="hand2")
        self.label.grid(row=0, column=2, sticky="ew")

        for widget in (self, self.indicator, self.icon, self.label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def _on_enter(self, _event=None):
        if not self._active:
            self.configure(fg_color=COLORS["sidebar_hover"])

    def _on_leave(self, _event=None):
        if not self._active:
            self.configure(fg_color="transparent")

    def _on_click(self, _event=None):
        self._command(self.key)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.configure(fg_color=COLORS["accent"] if active else "transparent")
        color = "#FFFFFF" if active else COLORS["sidebar_text"]
        self.icon.configure(text_color=color)
        self.label.configure(text_color=color)
        self.indicator.configure(
            fg_color="#FFFFFF" if active else "transparent")


class Sidebar(ctk.CTkFrame):
    """Barre latérale bleu profond avec navigation et bouton Quitter."""

    NAV_ITEMS = (
        ("Tableau de bord", "▦"),
        ("Catalogue", "▤"),
        ("Utilisateurs", "◉"),
        ("Emprunts", "↺"),
        ("Statistiques", "▥"),
        ("Données & sauvegarde", "◫"),
    )

    def __init__(self, master, on_select: Callable[[str], None],
                 on_quit: Callable[[], None]):
        super().__init__(master, fg_color=COLORS["sidebar"], corner_radius=0,
                         width=250)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._items: dict[str, NavItem] = {}

        self._build_brand()
        self._build_navigation(on_select)
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.grid(row=2, column=0, sticky="nsew")
        self._build_footer(on_quit)

    def _build_brand(self) -> None:
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=22, pady=(26, 28))
        brand.grid_columnconfigure(1, weight=1)

        logo = ctk.CTkFrame(brand, width=42, height=42, corner_radius=12,
                            fg_color=COLORS["accent"])
        logo.grid_propagate(False)
        logo.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        ctk.CTkLabel(logo, text="B", font=FONTS["brand"], text_color="#FFFFFF"
                     ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(brand, text="Bibliothèque", font=FONTS["brand"],
                     text_color="#FFFFFF", anchor="w").grid(
            row=0, column=1, sticky="w")
        ctk.CTkLabel(brand, text="Gestion personnelle", font=FONTS["brand_sub"],
                     text_color=COLORS["sidebar_muted"], anchor="w").grid(
            row=1, column=1, sticky="w")

    def _build_navigation(self, on_select: Callable[[str], None]) -> None:
        navigation = ctk.CTkFrame(self, fg_color="transparent")
        navigation.grid(row=1, column=0, sticky="ew")
        navigation.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(navigation, text="NAVIGATION", font=FONTS["caption"],
                     text_color=COLORS["sidebar_muted"], anchor="w").grid(
            row=0, column=0, sticky="w", padx=22, pady=(0, 8))

        for index, (label, symbol) in enumerate(self.NAV_ITEMS, start=1):
            item = NavItem(navigation, label, label, symbol, on_select)
            item.grid(row=index, column=0, sticky="ew", padx=12, pady=2)
            self._items[label] = item

    def _build_footer(self, on_quit: Callable[[], None]) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(footer, height=1, corner_radius=0,
                     fg_color="#27406E").grid(
            row=0, column=0, sticky="ew", pady=(0, 12))

        quit_button = ctk.CTkButton(
            footer, text="Quitter l'application", anchor="w",
            height=40, corner_radius=10, fg_color="transparent",
            hover_color="#3B2748", text_color="#FCA5A5",
            font=FONTS["body"], command=on_quit)
        quit_button.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(footer, text="Prototype · données locales",
                     font=FONTS["body_small"],
                     text_color=COLORS["sidebar_muted"]).grid(
            row=2, column=0, sticky="w", pady=(10, 0))

    def set_active(self, key: str) -> None:
        for label, item in self._items.items():
            item.set_active(label == key)


class Header(ctk.CTkFrame):
    """En-tête de page : titre, sous-titre, date et avatar."""

    def __init__(self, master, title: str, subtitle: str):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        left.grid_columnconfigure(0, weight=1)

        self._title = ctk.CTkLabel(left, text=title, font=FONTS["display"],
                                   text_color=COLORS["text"], anchor="w")
        self._title.grid(row=0, column=0, sticky="w")
        self._subtitle = ctk.CTkLabel(left, text=subtitle, font=FONTS["subtitle"],
                                      text_color=COLORS["text_muted"], anchor="w")
        self._subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        now = datetime.now()
        date_text = f"{now.day} {MOIS[now.month - 1]} {now.year}"
        ctk.CTkLabel(right, text=date_text, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).grid(
            row=0, column=0, padx=(0, 14))

        avatar = ctk.CTkFrame(right, width=42, height=42, corner_radius=21,
                              fg_color=COLORS["accent_soft"])
        avatar.grid_propagate(False)
        avatar.grid(row=0, column=1)
        ctk.CTkLabel(avatar, text="B", font=FONTS["body_bold"],
                     text_color=COLORS["accent"]).place(
            relx=0.5, rely=0.5, anchor="center")

    def set_content(self, title: str, subtitle: str) -> None:
        self._title.configure(text=title)
        self._subtitle.configure(text=subtitle)


class ActionCard(ctk.CTkFrame):
    """Carte cliquable utilisée pour les actions rapides."""

    def __init__(self, master, title: str, subtitle: str, symbol: str,
                 accent: str, soft: str, command: Callable[[], None]):
        super().__init__(master, fg_color=COLORS["surface_alt"],
                         corner_radius=12, border_width=1,
                         border_color=COLORS["border"], height=76)
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self._command = command
        self._accent = accent
        self._hover = False

        icon = ctk.CTkFrame(self, width=36, height=36, corner_radius=10,
                            fg_color=soft)
        icon.grid_propagate(False)
        icon.grid(row=0, column=0, padx=(12, 10), pady=20)
        ctk.CTkLabel(icon, text=symbol, font=FONTS["icon"],
                     text_color=accent).place(relx=0.5, rely=0.5, anchor="center")

        text = ctk.CTkFrame(self, fg_color="transparent")
        text.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(text, text=title, font=FONTS["action"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(text, text=subtitle, font=FONTS["action_sub"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=1, column=0, sticky="w", pady=(2, 0))

        self._bind_tree(self)

    def _bind_tree(self, widget) -> None:
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Button-1>", self._on_click)
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass
        for child in widget.winfo_children():
            self._bind_tree(child)

    def _on_enter(self, _event=None) -> None:
        self._hover = True
        self.configure(fg_color=COLORS["accent_soft"],
                       border_color=self._accent)

    def _on_leave(self, _event=None) -> None:
        self._hover = False
        self.configure(fg_color=COLORS["surface_alt"],
                       border_color=COLORS["border"])

    def _on_click(self, _event=None) -> None:
        self._command()


class Toast(ctk.CTkFrame):
    """Notification éphémère affichée en bas à droite."""

    def __init__(self, master, message: str, kind: str = "success"):
        palette = {
            "success": (COLORS["success"], COLORS["success_soft"], "✓"),
            "error": (COLORS["danger"], COLORS["danger_soft"], "!"),
            "info": (COLORS["accent"], COLORS["accent_soft"], "i"),
        }
        accent, soft, symbol = palette.get(kind, palette["info"])
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=12,
                         border_width=1, border_color=accent)

        icon = ctk.CTkFrame(self, width=30, height=30, corner_radius=9,
                            fg_color=soft)
        icon.grid_propagate(False)
        icon.grid(row=0, column=0, padx=(14, 10), pady=12)
        ctk.CTkLabel(icon, text=symbol, font=FONTS["icon_small"],
                     text_color=accent).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self, text=message, font=FONTS["body"],
                     text_color=COLORS["text"], justify="left",
                     anchor="w", wraplength=300).grid(
            row=0, column=1, sticky="w", padx=(0, 16), pady=12)


class BaseModal(ctk.CTkToplevel):
    """Fenêtre modale centrée, fermable par Échap et validable par Entrée."""

    def __init__(self, master, title: str, subtitle: str = "",
                 width: int = 480, height: int = 400,
                 confirm_text: str = "Confirmer", danger: bool = False,
                 on_success: Callable[[], None] | None = None):
        super().__init__(master)
        self.withdraw()
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(master.winfo_toplevel())
        self.protocol("WM_DELETE_WINDOW", self.close)

        self._width = width
        self._height = height
        self._on_success = on_success
        self.focus_widget = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 0))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=title, font=FONTS["title"],
                     text_color=COLORS["text"], anchor="w").grid(
            row=0, column=0, sticky="w")
        if subtitle:
            ctk.CTkLabel(header, text=subtitle, font=FONTS["subtitle"],
                         text_color=COLORS["text_muted"], anchor="w",
                         justify="left", wraplength=width - 48).grid(
                row=1, column=0, sticky="w", pady=(4, 0))

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(18, 0))
        self.body.grid_columnconfigure(0, weight=1)

        self.error_label = ctk.CTkLabel(
            self, text="", font=FONTS["body_small"],
            text_color=COLORS["danger"], anchor="w", justify="left",
            wraplength=width - 48)
        self.error_label.grid(row=2, column=0, sticky="ew", padx=24,
                              pady=(6, 0))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(6, 22))
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(footer, text="Annuler", height=40, width=110,
                      corner_radius=10, fg_color=COLORS["surface"],
                      hover_color=COLORS["surface_alt"],
                      border_width=1, border_color=COLORS["border"],
                      text_color=COLORS["text_muted"], font=FONTS["body"],
                      command=self.close).grid(row=0, column=1, padx=(0, 10))

        confirm_color = COLORS["danger"] if danger else COLORS["accent"]
        confirm_hover = "#991B1B" if danger else COLORS["accent_hover"]
        ctk.CTkButton(footer, text=confirm_text, height=40, width=150,
                      corner_radius=10, fg_color=confirm_color,
                      hover_color=confirm_hover, text_color="#FFFFFF",
                      font=FONTS["body_bold"],
                      command=self._submit).grid(row=0, column=2)

        self.bind("<Escape>", lambda _event: self.close())
        self.bind("<Return>", lambda _event: self._submit())
        self.after(30, self._present)

    def _present(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - self._width) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - self._height) // 2)
        self.geometry(f"{self._width}x{self._height}+{x}+{y}")
        self.deiconify()
        self.lift()
        self.grab_set()
        if self.focus_widget is not None:
            self.focus_widget.focus_set()
        else:
            self.focus_force()

    def add_field(self, row: int, label: str, placeholder: str = "") -> ctk.CTkEntry:
        wrapper = ctk.CTkFrame(self.body, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(wrapper, text=label, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=0, column=0, sticky="w", pady=(0, 5))
        entry = ctk.CTkEntry(
            wrapper, height=40, corner_radius=9,
            fg_color=COLORS["surface"], border_color=COLORS["border"],
            text_color=COLORS["text"], placeholder_text=placeholder,
            placeholder_text_color=COLORS["text_soft"], font=FONTS["body"])
        entry.grid(row=1, column=0, sticky="ew")
        return entry

    def add_option(self, row: int, label: str, values: list[str],
                   variable: StringVar) -> ctk.CTkOptionMenu:
        wrapper = ctk.CTkFrame(self.body, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(wrapper, text=label, font=FONTS["body_small"],
                     text_color=COLORS["text_muted"], anchor="w").grid(
            row=0, column=0, sticky="w", pady=(0, 5))
        menu = ctk.CTkOptionMenu(
            wrapper, values=values, variable=variable, height=40,
            corner_radius=9, fg_color=COLORS["surface"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            text_color=COLORS["text"], font=FONTS["body"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["accent_soft"],
            dropdown_text_color=COLORS["text"], dropdown_font=FONTS["body"])
        menu.grid(row=1, column=0, sticky="ew")
        return menu

    def _submit(self) -> None:
        error = self.validate()
        if error:
            self.error_label.configure(text=error)
            return
        callback = self._on_success
        self.close()
        if callback is not None:
            callback()

    def validate(self) -> str | None:
        return None

    def close(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


class ConfirmModal(BaseModal):
    """Boîte de confirmation simple."""

    def __init__(self, master, title: str, message: str,
                 confirm_text: str = "Confirmer", danger: bool = False,
                 on_confirm: Callable[[], None] | None = None):
        super().__init__(master, title, message, width=440, height=250,
                         confirm_text=confirm_text, danger=danger,
                         on_success=on_confirm)


class AddBookModal(BaseModal):
    """Formulaire d'ajout d'un livre."""

    def __init__(self, master, store: LibraryStore,
                 on_done: Callable[[str], None]):
        self.store = store
        self.on_done = on_done
        super().__init__(master, "Ajouter un livre",
                         "Renseignez les informations du nouvel ouvrage.",
                         width=480, height=440,
                         confirm_text="Ajouter le livre")
        self.title_entry = self.add_field(0, "Titre", "Ex. : Le Petit Prince")
        self.author_entry = self.add_field(1, "Auteur", "Ex. : Antoine de Saint-Exupéry")
        self.isbn_entry = self.add_field(2, "ISBN", "Ex. : 9782070612758")
        self.focus_widget = self.title_entry

    def validate(self) -> str | None:
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        if not title:
            return "Le titre est obligatoire."
        if not author:
            return "L'auteur est obligatoire."
        if not isbn:
            return "L'ISBN est obligatoire."
        try:
            self.store.add_book(Book(title, author, isbn))
        except ValueError as exc:
            return str(exc)
        self._on_success = lambda: self.on_done(
            f"« {title} » a été ajouté au catalogue.")
        return None


class AddUserModal(BaseModal):
    """Formulaire d'ajout d'un utilisateur."""

    def __init__(self, master, store: LibraryStore,
                 on_done: Callable[[str], None]):
        self.store = store
        self.on_done = on_done
        super().__init__(master, "Ajouter un utilisateur",
                         "Créez un nouveau compte emprunteur.",
                         width=480, height=400,
                         confirm_text="Créer le compte")
        self.name_entry = self.add_field(0, "Nom complet", "Ex. : Marie Dubois")
        self.id_entry = self.add_field(1, "Identifiant", "Ex. : USR021")
        self.focus_widget = self.name_entry

    def validate(self) -> str | None:
        name = self.name_entry.get().strip()
        user_id = self.id_entry.get().strip()
        if not name:
            return "Le nom est obligatoire."
        if not user_id:
            return "L'identifiant est obligatoire."
        try:
            self.store.add_user(User(name, user_id))
        except ValueError as exc:
            return str(exc)
        self._on_success = lambda: self.on_done(
            f"Le compte de {name} a été créé.")
        return None


class BorrowModal(BaseModal):
    """Sélection d'un livre disponible et de son emprunteur."""

    def __init__(self, master, store: LibraryStore,
                 on_done: Callable[[str], None],
                 book: Book | None = None):
        self.store = store
        self.on_done = on_done
        books = store.available_books()
        users = store.users
        self._books = {self._book_label(item): item for item in books}
        self._users = {f"{user.name} · {user.user_id}": user for user in users}

        super().__init__(master, "Emprunter un livre",
                         "Choisissez un ouvrage disponible et son emprunteur.",
                         width=520, height=420,
                         confirm_text="Enregistrer l'emprunt")

        book_values = list(self._books) or ["Aucun livre disponible"]
        user_values = list(self._users) or ["Aucun utilisateur"]
        selected_book = book_values[0]
        if book is not None:
            for label, candidate in self._books.items():
                if candidate is book:
                    selected_book = label
                    book_values = [label] + [value for value in book_values
                                             if value != label]
                    break
        self.book_var = StringVar(value=selected_book)
        self.user_var = StringVar(value=user_values[0])
        self.book_menu = self.add_option(0, "Livre", book_values, self.book_var)
        self.user_menu = self.add_option(1, "Emprunteur", user_values, self.user_var)
        self.focus_widget = self.book_menu

    @staticmethod
    def _book_label(book: Book) -> str:
        label = f"{book.title} · {book.isbn}"
        return label if len(label) <= 54 else f"{label[:51]}…"

    def validate(self) -> str | None:
        if not self._books:
            return "Aucun livre disponible pour l'emprunt."
        if not self._users:
            return "Aucun utilisateur enregistré."
        book = self._books.get(self.book_var.get())
        user = self._users.get(self.user_var.get())
        if book is None or user is None:
            return "Sélectionnez un livre et un utilisateur."
        try:
            self.store.borrow(book, user)
        except ValueError as exc:
            return str(exc)
        self._on_success = lambda: self.on_done(
            f"« {book.title} » est emprunté par {user.name}.")
        return None


class ReturnModal(BaseModal):
    """Sélection d'un emprunt en cours à clôturer."""

    def __init__(self, master, store: LibraryStore,
                 on_done: Callable[[str], None],
                 book: Book | None = None):
        self.store = store
        self.on_done = on_done
        self._books: dict[str, Book] = {}
        for item in store.borrowed_books():
            user = store.user_for(item)
            borrower = user.name if user else "Emprunteur inconnu"
            label = f"{item.title} — {borrower}"
            if len(label) > 58:
                label = f"{label[:55]}…"
            self._books[label] = item

        super().__init__(master, "Retourner un livre",
                         "Sélectionnez l'emprunt à clôturer.",
                         width=520, height=360,
                         confirm_text="Enregistrer le retour")

        values = list(self._books) or ["Aucun emprunt en cours"]
        selected_book = values[0]
        if book is not None:
            for label, candidate in self._books.items():
                if candidate is book:
                    selected_book = label
                    values = [label] + [value for value in values
                                        if value != label]
                    break
        self.book_var = StringVar(value=selected_book)
        self.book_menu = self.add_option(0, "Emprunt", values, self.book_var)
        self.focus_widget = self.book_menu

    def validate(self) -> str | None:
        if not self._books:
            return "Aucun emprunt en cours."
        book = self._books.get(self.book_var.get())
        if book is None:
            return "Sélectionnez un emprunt."
        try:
            self.store.return_book(book)
        except ValueError as exc:
            return str(exc)
        self._on_success = lambda: self.on_done(
            f"« {book.title} » a été retourné.")
        return None
