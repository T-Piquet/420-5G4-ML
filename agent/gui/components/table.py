"""Tableau defilant simple avec selection de ligne."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk


@dataclass(frozen=True)
class TableColumn:
    key: str
    label: str
    weight: int = 1
    wrap: int = 0


class ScrollableTable(ctk.CTkFrame):
    ROW_COLORS = (("gray94", "gray17"), ("gray97", "gray15"))
    SELECTED_COLOR = ("#cfe4ff", "#1e3a5f")

    def __init__(
        self,
        master,
        columns: list[TableColumn],
        *,
        status_key: str | None = None,
        status_colors: dict[str, tuple[str, str]] | None = None,
        empty_text: str = "Aucune donnée",
        on_select: Callable[[dict[str, object] | None], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columns = columns
        self.status_key = status_key
        self.status_colors = status_colors or {}
        self.empty_text = empty_text
        self.on_select = on_select
        self._row_widgets: list[ctk.CTkBaseClass] = []
        self._row_frames: list[ctk.CTkFrame] = []
        self._rows: list[dict[str, object]] = []
        self.selected_index: int | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(
            self,
            fg_color=("gray86", "gray20"),
            corner_radius=8,
        )
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        for index, column in enumerate(columns):
            self.header.grid_columnconfigure(index, weight=column.weight)
            label = ctk.CTkLabel(
                self.header,
                text=column.label,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("gray25", "gray80"),
            )
            label.grid(
                row=0, column=index, sticky="ew", padx=10, pady=8
            )

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.rows_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.rows_frame.grid(row=0, column=0, sticky="nsew")
        self.rows_frame.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Contenu
    # ------------------------------------------------------------------

    def set_rows(self, rows: list[dict[str, object]]) -> None:
        for widget in self._row_widgets:
            widget.destroy()
        self._row_widgets.clear()
        self._row_frames.clear()
        self._rows = list(rows)
        self.selected_index = None

        if not rows:
            empty = ctk.CTkLabel(
                self.rows_frame,
                text=self.empty_text,
                anchor="center",
                font=ctk.CTkFont(size=13),
                text_color=("gray45", "gray60"),
            )
            empty.grid(row=0, column=0, sticky="ew", pady=24)
            self._row_widgets.append(empty)
            self._notify_selection(None)
            return

        for row_index, row in enumerate(rows):
            row_frame = ctk.CTkFrame(
                self.rows_frame,
                fg_color=self.ROW_COLORS[row_index % 2],
                corner_radius=6,
            )
            row_frame.grid(row=row_index, column=0, sticky="ew", pady=2)

            for column_index, column in enumerate(self.columns):
                row_frame.grid_columnconfigure(
                    column_index, weight=column.weight
                )
                value = str(row.get(column.key, ""))
                text_color: str | tuple[str, str] = ("gray15", "gray88")
                if (
                    self.status_key == column.key
                    and value in self.status_colors
                ):
                    text_color = self.status_colors[value]

                label = ctk.CTkLabel(
                    row_frame,
                    text=value,
                    anchor="w",
                    justify="left",
                    font=ctk.CTkFont(size=12),
                    text_color=text_color,
                    wraplength=column.wrap,
                )
                label.grid(
                    row=0,
                    column=column_index,
                    sticky="ew",
                    padx=10,
                    pady=7,
                )

            self._bind_row(row_frame, row_index)
            self._row_frames.append(row_frame)
            self._row_widgets.append(row_frame)

        self._notify_selection(None)

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select_row(self, index: int) -> None:
        if not 0 <= index < len(self._row_frames):
            return

        self.selected_index = index
        for row_index, row_frame in enumerate(self._row_frames):
            row_frame.configure(
                fg_color=(
                    self.SELECTED_COLOR
                    if row_index == index
                    else self.ROW_COLORS[row_index % 2]
                )
            )

        self._notify_selection(self._rows[index])

    def clear_selection(self) -> None:
        self.selected_index = None
        for row_index, row_frame in enumerate(self._row_frames):
            row_frame.configure(fg_color=self.ROW_COLORS[row_index % 2])
        self._notify_selection(None)

    def get_selected(self) -> dict[str, object] | None:
        if self.selected_index is None:
            return None
        if not 0 <= self.selected_index < len(self._rows):
            return None
        return self._rows[self.selected_index]

    def _notify_selection(self, row: dict[str, object] | None) -> None:
        if self.on_select is not None:
            self.on_select(row)

    def _bind_row(self, widget, index: int) -> None:
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass

        widget.bind(
            "<Button-1>",
            lambda _event, row_index=index: self.select_row(row_index),
        )
        for child in widget.winfo_children():
            self._bind_row(child, index)
