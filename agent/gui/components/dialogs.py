"""Boites de dialogue modales : formulaires, confirmation et messages."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import customtkinter as ctk

from gui.service import BookView, LibraryError, UserView


class BaseDialog(ctk.CTkToplevel):
    """Fenetre modale centree sur la fenetre principale."""

    def __init__(
        self,
        master,
        title: str,
        *,
        width: int = 440,
        height: int = 320,
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self._dialog_width = width
        self._dialog_height = height
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda _event: self.destroy())
        self._first_focus: ctk.CTkBaseClass | None = None

        try:
            self.transient(master.winfo_toplevel())
            self.grab_set()
        except Exception:
            pass

        self.after(20, self._finish_setup)

    def _finish_setup(self) -> None:
        try:
            if not self.winfo_exists():
                return
            self._center()
            if self._first_focus is not None:
                self._first_focus.focus_set()
            else:
                self.focus_set()
        except Exception:
            pass

    def _center(self) -> None:
        try:
            parent = self.master.winfo_toplevel()
            x = (
                parent.winfo_rootx()
                + (parent.winfo_width() - self._dialog_width) // 2
            )
            y = (
                parent.winfo_rooty()
                + (parent.winfo_height() - self._dialog_height) // 2
            )
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

    def _run_action(
        self,
        action: Callable[[], None],
        error_label: ctk.CTkLabel,
    ) -> bool:
        """Execute une action, affiche l'erreur eventuelle et ferme si succes."""
        error_label.configure(text="")
        try:
            action()
        except LibraryError as exc:
            error_label.configure(text=str(exc))
            return False
        except Exception as exc:  # erreur inattendue : on ne ferme pas
            error_label.configure(text=f"Erreur inattendue : {exc}")
            return False

        self.destroy()
        return True

    def _make_error_label(self, master) -> ctk.CTkLabel:
        label = ctk.CTkLabel(
            master,
            text="",
            anchor="w",
            justify="left",
            wraplength=380,
            font=ctk.CTkFont(size=12),
            text_color=("#b91c1c", "#f87171"),
        )
        return label

    def _make_buttons(
        self,
        master,
        *,
        confirm_label: str,
        command: Callable[[], None],
        danger: bool = False,
        confirm_width: int = 140,
    ) -> None:
        buttons = ctk.CTkFrame(master, fg_color="transparent")
        buttons.grid(row=99, column=0, sticky="ew", padx=24, pady=(4, 20))
        buttons.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=110,
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "gray40"),
            text_color=("gray20", "gray85"),
            hover_color=("gray85", "gray25"),
            command=self.destroy,
        ).grid(row=0, column=1, padx=(0, 10))

        confirm_button = ctk.CTkButton(
            buttons,
            text=confirm_label,
            width=confirm_width,
            command=command,
        )
        if danger:
            confirm_button.configure(
                fg_color="#b91c1c", hover_color="#991b1b"
            )
        confirm_button.grid(row=0, column=2)


class FormDialog(BaseDialog):
    """Formulaire generique avec validation et message d'erreur integre."""

    def __init__(
        self,
        master,
        title: str,
        fields: Sequence[tuple[str, str, str]],
        on_submit: Callable[..., None],
        *,
        submit_label: str = "Enregistrer",
        intro: str | None = None,
    ) -> None:
        height = 210 + len(fields) * 62
        super().__init__(master, title, height=height)
        self.on_submit = on_submit
        self.entries: dict[str, ctk.CTkEntry] = {}
        self.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(
            row=0, column=0, sticky="nsew", padx=24, pady=(20, 8)
        )
        content.grid_columnconfigure(0, weight=1)

        row = 0
        if intro:
            ctk.CTkLabel(
                content,
                text=intro,
                anchor="w",
                justify="left",
                wraplength=380,
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray65"),
            ).grid(row=row, column=0, sticky="ew", pady=(0, 14))
            row += 1

        for key, label, placeholder in fields:
            ctk.CTkLabel(
                content,
                text=label,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=row, column=0, sticky="ew", pady=(0, 4))
            row += 1

            entry = ctk.CTkEntry(
                content,
                placeholder_text=placeholder,
                height=34,
            )
            entry.grid(row=row, column=0, sticky="ew", pady=(0, 10))
            entry.bind("<Return>", lambda _event: self.submit())
            self.entries[key] = entry
            if self._first_focus is None:
                self._first_focus = entry
            row += 1

        self.error_label = self._make_error_label(content)
        self.error_label.grid(row=row, column=0, sticky="ew", pady=(0, 4))

        self._make_buttons(
            self,
            confirm_label=submit_label,
            command=self.submit,
        )

    def submit(self) -> bool:
        values = {
            key: entry.get() for key, entry in self.entries.items()
        }
        return self._run_action(
            lambda: self.on_submit(**values), self.error_label
        )


class AddBookDialog(FormDialog):
    def __init__(
        self,
        master,
        on_submit: Callable[[str, str, str], None],
    ) -> None:
        super().__init__(
            master,
            "Ajouter un livre",
            [
                ("title", "Titre", "Ex. : Le Petit Prince"),
                (
                    "author",
                    "Auteur",
                    "Ex. : Antoine de Saint-Exupéry",
                ),
                ("isbn", "ISBN", "Ex. : 9782070612758"),
            ],
            on_submit,
            submit_label="Ajouter",
            intro="Renseignez les informations du nouveau livre.",
        )


class AddUserDialog(FormDialog):
    def __init__(
        self,
        master,
        on_submit: Callable[[str, str], None],
    ) -> None:
        super().__init__(
            master,
            "Nouvel adhérent",
            [
                ("name", "Nom", "Ex. : Marie Dubois"),
                ("user_id", "Identifiant", "Ex. : USR042"),
            ],
            on_submit,
            submit_label="Ajouter",
            intro="Renseignez l'identité du nouvel adhérent.",
        )


class CheckoutDialog(BaseDialog):
    """Selection d'un livre disponible et de l'adherent emprunteur."""

    def __init__(
        self,
        master,
        books: Sequence[BookView],
        users: Sequence[UserView],
        on_submit: Callable[[str, str], None],
    ) -> None:
        super().__init__(master, "Nouvel emprunt", height=380)
        self.on_submit = on_submit

        self._isbn_by_label = {
            f"{book.isbn} — {book.title}": book.isbn for book in books
        }
        self._user_by_label = {
            f"{user.user_id} — {user.name}": user.user_id
            for user in users
        }

        self.grid_rowconfigure(0, weight=1)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(
            row=0, column=0, sticky="nsew", padx=24, pady=(20, 8)
        )
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content,
            text=(
                "Sélectionnez un livre disponible et l'adhérent "
                "qui l'emprunte."
            ),
            anchor="w",
            justify="left",
            wraplength=380,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray65"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(
            content,
            text="Livre",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=1, column=0, sticky="ew", pady=(0, 4))

        self.book_combo = ctk.CTkComboBox(
            content,
            values=list(self._isbn_by_label),
            height=34,
        )
        self.book_combo.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        if self._isbn_by_label:
            self.book_combo.set(next(iter(self._isbn_by_label)))

        ctk.CTkLabel(
            content,
            text="Adhérent",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=3, column=0, sticky="ew", pady=(0, 4))

        self.user_combo = ctk.CTkComboBox(
            content,
            values=list(self._user_by_label),
            height=34,
        )
        self.user_combo.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        if self._user_by_label:
            self.user_combo.set(next(iter(self._user_by_label)))

        self.error_label = self._make_error_label(content)
        self.error_label.grid(row=5, column=0, sticky="ew", pady=(0, 4))

        self._make_buttons(
            self,
            confirm_label="Emprunter",
            command=self.submit,
            confirm_width=150,
        )

        self._first_focus = self.book_combo
        self.book_combo.bind("<Return>", lambda _event: self.submit())
        self.user_combo.bind("<Return>", lambda _event: self.submit())

    def _resolve(
        self,
        combo: ctk.CTkComboBox,
        mapping: dict[str, str],
    ) -> str:
        value = combo.get().strip()
        return mapping.get(value, value)

    def submit(self) -> bool:
        isbn = self._resolve(self.book_combo, self._isbn_by_label)
        user_id = self._resolve(self.user_combo, self._user_by_label)

        if not isbn:
            self.error_label.configure(
                text="Veuillez sélectionner un livre."
            )
            return False
        if not user_id:
            self.error_label.configure(
                text="Veuillez sélectionner un adhérent."
            )
            return False

        return self._run_action(
            lambda: self.on_submit(isbn, user_id), self.error_label
        )


class ConfirmDialog(BaseDialog):
    """Confirmation d'une action destructive."""

    def __init__(
        self,
        master,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        *,
        confirm_label: str = "Confirmer",
        danger: bool = True,
    ) -> None:
        super().__init__(master, title, height=280)
        self.on_confirm = on_confirm
        self.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(
            row=0, column=0, sticky="nsew", padx=24, pady=(24, 8)
        )
        content.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="⚠",
            width=32,
            font=ctk.CTkFont(size=26),
            text_color="#f59e0b",
        ).grid(row=0, column=0, sticky="n", padx=(0, 12))

        ctk.CTkLabel(
            content,
            text=message,
            anchor="w",
            justify="left",
            wraplength=340,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, sticky="ew")

        self.error_label = self._make_error_label(content)
        self.error_label.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(12, 4)
        )

        self._make_buttons(
            self,
            confirm_label=confirm_label,
            command=self.confirm,
            danger=danger,
        )

    def confirm(self) -> bool:
        return self._run_action(self.on_confirm, self.error_label)


class MessageDialog(BaseDialog):
    """Boite de message simple (erreur, information, succes)."""

    STYLES = {
        "error": ("✕", "#ef4444"),
        "info": ("ℹ", "#3b82f6"),
        "success": ("✓", "#22c55e"),
    }

    def __init__(
        self,
        master,
        title: str,
        message: str,
        *,
        kind: str = "info",
    ) -> None:
        super().__init__(master, title, height=250)
        self.grid_rowconfigure(0, weight=1)

        icon, color = self.STYLES.get(kind, self.STYLES["info"])
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(
            row=0, column=0, sticky="nsew", padx=24, pady=(24, 8)
        )
        content.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text=icon,
            width=32,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=color,
        ).grid(row=0, column=0, sticky="n", padx=(0, 12))

        ctk.CTkLabel(
            content,
            text=message,
            anchor="w",
            justify="left",
            wraplength=350,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, sticky="ew")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=1, column=0, sticky="ew", padx=24, pady=(4, 20))
        buttons.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            buttons,
            text="Fermer",
            width=120,
            command=self.destroy,
        ).grid(row=0, column=1)


def show_error(master, message: str, *, title: str = "Erreur") -> None:
    MessageDialog(master, title, message, kind="error")


def show_info(master, message: str, *, title: str = "Information") -> None:
    MessageDialog(master, title, message, kind="info")
