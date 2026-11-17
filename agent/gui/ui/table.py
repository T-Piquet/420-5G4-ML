"""Scrollable container for list/table rows."""

import customtkinter as ctk


class ScrollableList(ctk.CTkScrollableFrame):
    """Scrollable vertical list of row widgets."""

    def __init__(self, master, fg_color: str = "transparent") -> None:
        super().__init__(master, fg_color=fg_color)
        self.grid_columnconfigure(0, weight=1)
        self._rows: list[ctk.CTkBaseClass] = []

    def clear(self) -> None:
        for row in self._rows:
            row.destroy()
        self._rows.clear()

    def add_row(self, widget: ctk.CTkBaseClass) -> None:
        idx = len(self._rows)
        widget.grid(row=idx, column=0, padx=6, pady=6, sticky="ew")
        self._rows.append(widget)
