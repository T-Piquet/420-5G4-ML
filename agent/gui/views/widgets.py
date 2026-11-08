"""Composants réutilisables de l'interface."""
from collections.abc import Callable
from typing import NamedTuple

import customtkinter as ctk

from gui.views import theme

_BUTTON_STYLES = {
    "primary": {
        "fg_color": theme.GREEN,
        "hover_color": theme.GREEN_DARK,
        "text_color": theme.SURFACE,
        "border_width": 0,
    },
    "secondary": {
        "fg_color": theme.SURFACE,
        "hover_color": theme.SURFACE_ALT,
        "text_color": theme.TEXT,
        "border_width": 1,
        "border_color": theme.LINE,
    },
    "ghost": {
        "fg_color": "transparent",
        "hover_color": theme.SURFACE_ALT,
        "text_color": theme.GREEN_TEXT,
        "border_width": 0,
    },
    "danger": {
        "fg_color": theme.DANGER,
        "hover_color": theme.DANGER_DARK,
        "text_color": theme.SURFACE,
        "border_width": 0,
    },
}
_SEARCH_DELAY_MS = 180


def make_button(master, text: str, command: Callable[[], None], variant: str = "secondary",
                small: bool = False, **options) -> ctk.CTkButton:
    options.setdefault("width", 0)
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        height=28 if small else 38,
        corner_radius=theme.RADIUS_SMALL,
        font=theme.font("button_small" if small else "button"),
        text_color_disabled=theme.DISABLED,
        **_BUTTON_STYLES[variant],
        **options,
    )


def make_label(master, text: str = "", role: str = "body", color: str = theme.TEXT,
               **options) -> ctk.CTkLabel:
    return ctk.CTkLabel(master, text=text, font=theme.font(role), text_color=color, **options)


class Panel(ctk.CTkFrame):
    """Surface blanche délimitée, avec un titre facultatif."""

    def __init__(self, master, title: str = "", subtitle: str = "") -> None:
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.LINE,
            border_width=1,
            corner_radius=theme.RADIUS,
        )
        self.grid_columnconfigure(0, weight=1)
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid_columnconfigure(0, weight=1)
        if title:
            self.header.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 10))
            make_label(self.header, title, "heading", theme.INK, anchor="w").grid(
                row=0, column=0, sticky="w"
            )
        if subtitle:
            make_label(self.header, subtitle, "small", theme.MUTED, anchor="w").grid(
                row=1, column=0, sticky="w"
            )


class PageHeader(ctk.CTkFrame):
    """Titre de page, sous-titre et actions principales."""

    def __init__(self, master, title: str, subtitle: str) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        make_label(self, title, "display", theme.INK, anchor="w").grid(row=0, column=0, sticky="w")
        self.subtitle = make_label(self, subtitle, "body", theme.MUTED, anchor="w")
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.actions = ctk.CTkFrame(self, fg_color="transparent", width=1, height=1)
        self.actions.grid(row=0, column=1, rowspan=2, sticky="e")

    def add_action(self, text: str, command: Callable[[], None],
                   variant: str = "secondary") -> ctk.CTkButton:
        button = make_button(self.actions, text, command, variant)
        button.pack(side="left", padx=(10, 0))
        return button


class SearchCriterion(NamedTuple):
    label: str
    placeholder: str
    live: bool  # False : recherche exacte, lancée seulement avec Entrée.


class SearchBar(ctk.CTkFrame):
    """Champ de recherche avec choix du critère."""

    def __init__(self, master, criteria: list[SearchCriterion],
                 on_search: Callable[[], None]) -> None:
        super().__init__(master, fg_color="transparent")
        self._criteria = {criterion.label: criterion for criterion in criteria}
        self._on_search = on_search
        self._pending: str | None = None
        self._selector: ctk.CTkSegmentedButton | None = None
        self.grid_columnconfigure(1, weight=1)

        if len(criteria) > 1:
            choice = ctk.CTkFrame(self, fg_color="transparent")
            choice.grid(row=0, column=0, padx=(0, 10))
            make_label(choice, "Chercher par", "small", theme.MUTED).pack(side="left", padx=(0, 8))
            self._selector = make_segments(
                choice, [criterion.label for criterion in criteria], self._on_criterion_changed
            )
            self._selector.pack(side="left")

        self._entry = ctk.CTkEntry(
            self,
            height=38,
            corner_radius=theme.RADIUS_SMALL,
            border_width=1,
            border_color=theme.LINE,
            fg_color=theme.SURFACE,
            text_color=theme.INK,
            placeholder_text_color=theme.MUTED,
            placeholder_text=criteria[0].placeholder,
            font=theme.font("body"),
        )
        self._entry.grid(row=0, column=1, sticky="ew")
        self._entry.bind("<KeyRelease>", self._on_key_release)
        self._entry.bind("<Return>", lambda _event: self._search_now())
        make_button(self, "Effacer", self.clear, "ghost").grid(row=0, column=2, padx=(6, 0))

    @property
    def criterion(self) -> str:
        return self._selector.get() if self._selector else next(iter(self._criteria))

    @property
    def query(self) -> str:
        return self._entry.get().strip()

    def clear(self) -> None:
        self._entry.delete(0, "end")
        self._search_now()

    def focus_entry(self) -> None:
        self._entry.focus_set()

    def _on_criterion_changed(self, label: str) -> None:
        self._entry.configure(placeholder_text=self._criteria[label].placeholder)
        self._search_now()

    def _on_key_release(self, event) -> None:
        if event.keysym == "Return":
            return
        if self._criteria[self.criterion].live or not self.query:
            self._cancel_pending()
            self._pending = self.after(_SEARCH_DELAY_MS, self._search_now)

    def _search_now(self) -> None:
        self._cancel_pending()
        self._on_search()

    def _cancel_pending(self) -> None:
        if self._pending is not None:
            self.after_cancel(self._pending)
            self._pending = None


def make_segments(master, values: list[str],
                  command: Callable[[str], None]) -> ctk.CTkSegmentedButton:
    segments = ctk.CTkSegmentedButton(
        master,
        values=values,
        command=command,
        height=38,
        corner_radius=theme.RADIUS_SMALL,
        border_width=2,
        fg_color=theme.LINE,
        selected_color=theme.GREEN_PALE,
        selected_hover_color=theme.GREEN_PALE,
        unselected_color=theme.SURFACE,
        unselected_hover_color=theme.SURFACE_ALT,
        text_color=theme.INK,
        text_color_disabled=theme.DISABLED,
        font=theme.font("button_small"),
    )
    segments.set(values[0])
    return segments


class Toast(ctk.CTkLabel):
    """Message temporaire en bas à droite de la fenêtre."""

    _DURATION_MS = 4000

    def __init__(self, master) -> None:
        super().__init__(
            master,
            text="",
            font=theme.font("strong"),
            text_color=theme.SURFACE,
            corner_radius=theme.RADIUS_SMALL,
            wraplength=420,
            justify="left",
        )
        self._timer: str | None = None

    def show(self, message: str, is_error: bool = False) -> None:
        self.configure(
            text=f"  {message}  ",
            fg_color=theme.DANGER if is_error else theme.GREEN_DARK,
            height=46,
        )
        self.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")
        self.lift()
        if self._timer is not None:
            self.after_cancel(self._timer)
        self._timer = self.after(self._DURATION_MS, self.place_forget)
