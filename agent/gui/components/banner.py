"""Banniere de notification (succes, erreur, information)."""

from __future__ import annotations

import customtkinter as ctk


class Banner(ctk.CTkFrame):
    """Bandeau discret affiche en haut de la zone principale."""

    STYLES = {
        "success": {
            "fg_color": ("#dcfce7", "#14532d"),
            "text_color": ("#166534", "#bbf7d0"),
            "icon": "✓",
        },
        "error": {
            "fg_color": ("#fee2e2", "#7f1d1d"),
            "text_color": ("#991b1b", "#fecaca"),
            "icon": "✕",
        },
        "info": {
            "fg_color": ("#dbeafe", "#1e3a8a"),
            "text_color": ("#1d4ed8", "#bfdbfe"),
            "icon": "ℹ",
        },
    }

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            corner_radius=8,
            height=40,
            fg_color=self.STYLES["info"]["fg_color"],
            **kwargs,
        )
        self.grid_columnconfigure(1, weight=1)

        self.icon_label = ctk.CTkLabel(
            self,
            text="",
            width=24,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.icon_label.grid(row=0, column=0, padx=(14, 4), pady=8)

        self.message_label = ctk.CTkLabel(
            self,
            text="",
            anchor="w",
            justify="left",
            font=ctk.CTkFont(size=13),
        )
        self.message_label.grid(
            row=0, column=1, sticky="ew", padx=(0, 10), pady=8
        )

        self.close_button = ctk.CTkButton(
            self,
            text="✕",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            command=self.hide,
        )
        self.close_button.grid(row=0, column=2, padx=(0, 10))

        self._job: str | None = None

    def show(
        self,
        message: str,
        kind: str = "success",
        duration: int = 5000,
    ) -> None:
        style = self.STYLES.get(kind, self.STYLES["info"])
        self.configure(fg_color=style["fg_color"])
        self.icon_label.configure(
            text=style["icon"], text_color=style["text_color"]
        )
        self.message_label.configure(
            text=message, text_color=style["text_color"]
        )
        self.close_button.configure(
            text_color=style["text_color"],
            hover_color=style["fg_color"],
        )

        self.grid()
        self.tkraise()

        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        if duration > 0:
            self._job = self.after(duration, self.hide)

    def hide(self) -> None:
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        self.grid_remove()
