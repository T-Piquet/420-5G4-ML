"""Reusable row card widgets matching the Bibliothèque mockups."""

from typing import Callable, Optional
import customtkinter as ctk

from theme import COLORS, FONTS, RADIUS
from ui.icons import ICON_DELETE, ICON_EDIT


class ItemRowCard(ctk.CTkFrame):
    """Horizontal row card showing item info and optional delete/edit actions."""

    def __init__(
        self,
        master,
        text: str,
        on_delete: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(
            master,
            height=44,
            corner_radius=RADIUS["row"],
            fg_color=COLORS["bg_row"],
        )
        self.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            self,
            text=text,
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        label.grid(row=0, column=0, padx=16, pady=8, sticky="ew")

        col = 1
        if on_delete is not None:
            del_btn = ctk.CTkButton(
                self,
                text=ICON_DELETE,
                width=36,
                height=30,
                corner_radius=RADIUS["button"],
                fg_color="transparent",
                hover_color=COLORS["bg_button_hover"],
                text_color=COLORS["text_primary"],
                font=FONTS["body"],
                command=on_delete,
            )
            del_btn.grid(row=0, column=col, padx=(4, 8), pady=6)
            col += 1

        if on_edit is not None:
            edit_btn = ctk.CTkButton(
                self,
                text=ICON_EDIT,
                width=96,
                height=30,
                corner_radius=RADIUS["button"],
                fg_color=COLORS["bg_white_btn"],
                hover_color=COLORS["bg_white_btn_hover"],
                text_color=COLORS["text_primary"],
                font=FONTS["body"],
                command=on_edit,
            )
            edit_btn.grid(row=0, column=col, padx=(4, 12), pady=6)
