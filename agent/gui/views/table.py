"""Tableau de données ; les lignes sont réutilisées pour rester fluide."""
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

import customtkinter as ctk

from gui.views import theme
from gui.views.widgets import make_button, make_label

_SCROLLBAR_GUTTER = 18


class CellKind(Enum):
    TEXT = "text"
    TWO_LINES = "two_lines"
    STATUS = "status"
    ACTIONS = "actions"


class Column(NamedTuple):
    title: str
    weight: int
    kind: CellKind = CellKind.TEXT
    max_chars: int = 34


@dataclass(frozen=True)
class TwoLines:
    title: str
    subtitle: str


@dataclass(frozen=True)
class Status:
    text: str
    positive: bool


@dataclass(frozen=True)
class Action:
    label: str
    command: Callable[[], None]
    enabled: bool = True


def _shorten(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else f"{text[:max_chars - 1].rstrip()}…"


class _ActionsCell(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self._buttons: list[ctk.CTkButton] = []

    def show(self, actions: Sequence[Action]) -> None:
        while len(self._buttons) < len(actions):
            button = make_button(self, "", lambda: None, small=True)
            button.pack(side="left", padx=(0, 6))
            self._buttons.append(button)
        for button, action in zip(self._buttons, actions):
            button.configure(
                text=action.label,
                command=action.command,
                state="normal" if action.enabled else "disabled",
            )


class _Row(ctk.CTkFrame):
    def __init__(self, master, columns: Sequence[Column]) -> None:
        super().__init__(master, fg_color="transparent")
        self._columns = columns
        ctk.CTkFrame(self, height=1, fg_color=theme.LINE, corner_radius=0).pack(fill="x")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=9)
        self._cells = []
        for index, column in enumerate(columns):
            body.grid_columnconfigure(index, weight=column.weight, uniform="table")
            cell = self._build_cell(body, column)
            cell[0].grid(row=0, column=index, sticky="w", padx=(0, 12))
            self._cells.append(cell)

    @staticmethod
    def _build_cell(master, column: Column) -> tuple:
        if column.kind is CellKind.TWO_LINES:
            frame = ctk.CTkFrame(master, fg_color="transparent")
            title = make_label(frame, "", "strong", theme.INK, anchor="w", height=20)
            subtitle = make_label(frame, "", "small", theme.MUTED, anchor="w", height=18)
            title.pack(anchor="w")
            subtitle.pack(anchor="w")
            return (frame, title, subtitle)
        if column.kind is CellKind.STATUS:
            pill = make_label(master, "", "button_small", corner_radius=6, height=26)
            return (pill,)
        if column.kind is CellKind.ACTIONS:
            return (_ActionsCell(master),)
        return (make_label(master, "", "body", theme.TEXT, anchor="w"),)

    def show(self, values: Sequence) -> None:
        for column, cell, value in zip(self._columns, self._cells, values):
            if column.kind is CellKind.TWO_LINES:
                cell[1].configure(text=_shorten(value.title, column.max_chars))
                cell[2].configure(text=_shorten(value.subtitle, column.max_chars))
            elif column.kind is CellKind.STATUS:
                cell[0].configure(
                    text=f"  {value.text}  ",
                    fg_color=theme.GREEN_PALE if value.positive else theme.OCHRE_PALE,
                    text_color=theme.GREEN_TEXT if value.positive else theme.OCHRE_TEXT,
                )
            elif column.kind is CellKind.ACTIONS:
                cell[0].show(value)
            else:
                cell[0].configure(text=_shorten(value, column.max_chars))


class DataTable(ctk.CTkFrame):
    """En-tête fixe et corps, défilant si `scrollable` est vrai."""

    def __init__(self, master, columns: Sequence[Column], scrollable: bool = True) -> None:
        super().__init__(master, fg_color="transparent")
        self._columns = columns
        self._rows: list[_Row] = []
        self._scrollable = scrollable
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=theme.SURFACE_ALT, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        labels = ctk.CTkFrame(header, fg_color="transparent")
        labels.pack(fill="x", padx=(22, 22 + (_SCROLLBAR_GUTTER if scrollable else 0)))
        for index, column in enumerate(columns):
            labels.grid_columnconfigure(index, weight=column.weight, uniform="table")
            make_label(labels, column.title, "button_small", theme.MUTED, anchor="w", height=34).grid(
                row=0, column=index, sticky="w", padx=(0, 12)
            )

        self._body = (
            ctk.CTkScrollableFrame(
                self, fg_color="transparent", corner_radius=0,
                scrollbar_button_color=theme.SCROLLBAR,
                scrollbar_button_hover_color=theme.MUTED,
            )
            if scrollable
            else ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        )
        self._body.grid(row=1, column=0, sticky="nsew")
        self._empty = make_label(self._body, "", "body", theme.MUTED, justify="center")

    def set_rows(self, rows: Sequence[Sequence], empty_text: str = "") -> None:
        while len(self._rows) < len(rows):
            self._rows.append(_Row(self._body, self._columns))
        for index, row in enumerate(self._rows):
            if index < len(rows):
                row.show(rows[index])
                if not row.winfo_manager():
                    row.pack(fill="x")
            else:
                row.pack_forget()
        if rows:
            self._empty.pack_forget()
        else:
            self._empty.configure(text=empty_text)
            self._empty.pack(pady=36, padx=24)
        if self._scrollable:
            self._body._parent_canvas.yview_moveto(0)
