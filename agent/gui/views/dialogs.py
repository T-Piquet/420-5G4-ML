"""Fenêtres modales : formulaires et confirmations."""
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import customtkinter as ctk

from gui.views import theme
from gui.views.widgets import make_button, make_label

_WIDTH = 480
_INNER_WIDTH = _WIDTH - 56


@dataclass(frozen=True)
class TextField:
    name: str
    label: str
    placeholder: str = ""


@dataclass(frozen=True)
class ChoiceField:
    name: str
    label: str
    choices: Sequence[tuple[str, str]]  # (valeur, texte affiché)
    selected: str = ""
    placeholder: str = "Sélectionner"


@dataclass(frozen=True)
class DialogButton:
    label: str
    command: Callable[[], None] | None = None
    variant: str = "secondary"


class _Modal(ctk.CTkToplevel):
    def __init__(self, parent, title: str, description: str) -> None:
        super().__init__(parent, fg_color=theme.SURFACE)
        self._parent = parent
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=28, pady=24)
        make_label(self.body, title, "heading", theme.INK, anchor="w").pack(anchor="w")
        make_label(
            self.body, description, "body", theme.MUTED, anchor="w", justify="left",
            wraplength=_INNER_WIDTH,
        ).pack(anchor="w", pady=(4, 12))
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", lambda _event: self.close())

    def present(self) -> None:
        """Centre la fenêtre sur son parent, puis capture le clavier et la souris."""
        self.update_idletasks()
        x = self._parent.winfo_rootx() + (self._parent.winfo_width() - self.winfo_reqwidth()) // 2
        y = self._parent.winfo_rooty() + (self._parent.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.wait_visibility()
        self.grab_set()

    def close(self) -> None:
        self.grab_release()
        self.destroy()
        self._parent.focus_set()

    def add_footer(self, buttons: Sequence[tuple[str, Callable[[], None], str]]) -> None:
        footer = ctk.CTkFrame(self.body, fg_color="transparent")
        footer.pack(anchor="e", pady=(18, 0))
        for label, command, variant in buttons:
            make_button(footer, label, command, variant).pack(side="left", padx=(8, 0))


class FormDialog(_Modal):
    """Formulaire ; `on_submit` reçoit les valeurs et ce dialogue."""

    def __init__(self, parent, title: str, description: str, submit_label: str,
                 fields: Sequence[TextField | ChoiceField],
                 on_submit: Callable[[dict[str, str], "FormDialog"], None]) -> None:
        super().__init__(parent, title, description)
        self._fields = fields
        self._on_submit = on_submit
        self._readers: dict[str, Callable[[], str]] = {}
        self._first_input = None
        for field in fields:
            self._add_field(field)
        self._error = make_label(
            self.body, "", "strong", theme.DANGER, anchor="w", justify="left",
            wraplength=_INNER_WIDTH,
        )
        self._footer_anchor = ctk.CTkFrame(self.body, fg_color="transparent", height=0)
        self._footer_anchor.pack(fill="x")
        self.add_footer([("Annuler", self.close, "secondary"), (submit_label, self._submit, "primary")])
        self.bind("<Return>", lambda _event: self._submit())
        self.present()
        if self._first_input is not None:
            self._first_input.focus_set()

    def show_error(self, message: str) -> None:
        self._error.configure(text=message)
        self._error.pack(anchor="w", pady=(10, 0), before=self._footer_anchor)

    def _add_field(self, field: TextField | ChoiceField) -> None:
        make_label(self.body, field.label, "strong", theme.TEXT, anchor="w").pack(
            anchor="w", pady=(8, 2)
        )
        if isinstance(field, TextField):
            control = ctk.CTkEntry(
                self.body, width=_INNER_WIDTH, height=40, corner_radius=theme.RADIUS_SMALL,
                border_width=1, border_color=theme.LINE, fg_color=theme.SURFACE,
                text_color=theme.INK, placeholder_text=field.placeholder,
                placeholder_text_color=theme.MUTED, font=theme.font("body"),
            )
            self._readers[field.name] = lambda entry=control: entry.get().strip()
            self._first_input = self._first_input or control
        else:
            texts = {text: value for value, text in field.choices}
            selected_text = next(
                (text for value, text in field.choices if value == field.selected),
                field.placeholder,
            )
            control = ctk.CTkOptionMenu(
                self.body, width=_INNER_WIDTH, height=40, corner_radius=theme.RADIUS_SMALL,
                values=list(texts), fg_color=theme.SURFACE_ALT, button_color=theme.LINE,
                button_hover_color=theme.GREEN_PALE, text_color=theme.INK,
                dropdown_fg_color=theme.SURFACE, dropdown_text_color=theme.INK,
                dropdown_hover_color=theme.GREEN_PALE, font=theme.font("body"),
                dropdown_font=theme.font("body"), dynamic_resizing=False,
            )
            control.set(selected_text)
            self._readers[field.name] = lambda menu=control, mapping=texts: mapping.get(menu.get(), "")
        control.pack(fill="x")

    def _submit(self) -> None:
        values = {name: read() for name, read in self._readers.items()}
        for field in self._fields:
            if not values[field.name]:
                self.show_error(f"Renseignez le champ « {field.label} ».")
                return
        self._on_submit(values, self)


class ConfirmDialog(_Modal):
    """Question fermée dont chaque bouton ferme le dialogue."""

    def __init__(self, parent, title: str, message: str, buttons: Sequence[DialogButton]) -> None:
        super().__init__(parent, title, message)
        self.add_footer([
            (button.label, lambda chosen=button: self._choose(chosen), button.variant)
            for button in buttons
        ])
        self.present()
        self.focus_set()

    def _choose(self, button: DialogButton) -> None:
        self.close()
        if button.command is not None:
            button.command()
