"""Left navigation sidebar for the Bibliothèque GUI."""

from typing import Callable, Dict, Tuple
import customtkinter as ctk

from theme import COLORS, FONTS, RADIUS


class NavBar(ctk.CTkFrame):
    """Vertical sidebar with page navigation buttons."""

    def __init__(
        self,
        master,
        items: Tuple[Tuple[str, str], ...],
        on_select: Callable[[str], None],
    ) -> None:
        super().__init__(master, width=210, corner_radius=0, fg_color=COLORS["bg_sidebar"])
        self.grid_propagate(False)
        self._on_select = on_select
        self._buttons: Dict[str, ctk.CTkButton] = {}

        for idx, (key, label) in enumerate(items):
            btn = ctk.CTkButton(
                self,
                text=label,
                height=42,
                corner_radius=RADIUS["button"],
                fg_color=COLORS["bg_button"],
                hover_color=COLORS["bg_button_hover"],
                text_color=COLORS["text_primary"],
                font=FONTS["nav"],
                command=lambda k=key: self._on_select(k),
            )
            btn.grid(row=idx, column=0, padx=14, pady=(14 if idx == 0 else 6, 6), sticky="ew")
            self._buttons[key] = btn

        self.grid_columnconfigure(0, weight=1)

    def set_active(self, active_key: str) -> None:
        for key, btn in self._buttons.items():
            if key == active_key:
                btn.configure(fg_color=COLORS["bg_button_active"])
            else:
                btn.configure(fg_color=COLORS["bg_button"])
