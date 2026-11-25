"""Panneaux latéraux modaux, modèle commun aux formulaires."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk

import theme
from data_store import LibraryStore, StoreError, User


class SidePanel(ctk.CTkToplevel):
    """Panneau latéral modal aligné à droite, sous le bandeau."""

    TITLE = ""
    WIDTH = 400

    def __init__(self, parent: ctk.CTkBaseClass) -> None:
        super().__init__(parent, fg_color=theme.BACKGROUND)
        self.parent = parent
        self.overrideredirect(True)
        self.transient(parent)
        self.bind("<Escape>", lambda _event: self.close())
        self._closed = False
        self._initial_focus: ctk.CTkBaseClass | None = None

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(
            content,
            text=self.TITLE,
            font=theme.font(20, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).pack(fill="x", pady=(0, 24))

        body = ctk.CTkFrame(content, fg_color="transparent")
        body.pack(fill="both", expand=True)
        self._build_form(body)

    def _build_form(self, body: ctk.CTkFrame) -> None:
        """À redéfinir : construit le contenu du formulaire."""
        raise NotImplementedError

    def show(self) -> None:
        """Aligne le panneau à droite, sous le bandeau, et bloque la page."""
        self.update_idletasks()
        height = max(self.parent.winfo_height() - theme.HEADER_HEIGHT, 320)
        x = self.parent.winfo_rootx() + self.parent.winfo_width() - self.WIDTH
        y = self.parent.winfo_rooty() + theme.HEADER_HEIGHT
        self.geometry(f"{self.WIDTH}x{height}+{x}+{y}")
        self.wait_visibility()
        try:
            self.grab_set()
        except tk.TclError:
            # Un autre client X (par exemple une autre instance de la GUI)
            # détient le grab : le panneau reste utilisable, simplement non
            # modal. Ne pas laisser l'exception interrompre l'affichage.
            pass
        self.lift()
        self.focus_force()
        if self._initial_focus is not None:
            self._initial_focus.focus_set()

    @property
    def is_open(self) -> bool:
        return not self._closed

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class AddUserPanel(SidePanel):
    """Formulaire d'ajout d'utilisateur."""

    TITLE = "Ajouter un utilisateur"

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        store: LibraryStore,
        on_saved: Callable[[User], None],
    ) -> None:
        super().__init__(parent)
        self.store = store
        self.on_saved = on_saved

    def _build_form(self, body: ctk.CTkFrame) -> None:
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            body,
            text="Nom",
            font=theme.font(15, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.name_entry = ctk.CTkEntry(
            body,
            height=40,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.SURFACE,
            text_color=theme.TEXT,
            placeholder_text="Nom ici",
            placeholder_text_color=theme.TEXT_MUTED,
            font=theme.font(14),
        )
        self.name_entry.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(
            body,
            text="L'identifiant sera généré automatiquement.",
            font=theme.font(11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", pady=(6, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="e")

        ctk.CTkButton(
            buttons,
            text="Annuler",
            font=theme.font(14),
            width=100,
            height=36,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.SURFACE,
            hover_color=theme.HOVER,
            text_color=theme.TEXT,
            command=self.close,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            buttons,
            text="Ajouter",
            font=theme.font(14),
            width=110,
            height=36,
            corner_radius=theme.CORNER_RADIUS,
            border_width=0,
            fg_color=theme.SAGE,
            hover_color=theme.SAGE_HOVER,
            text_color=theme.BACKGROUND,
            command=self._submit,
        ).pack(side="left")

        self.message_label = ctk.CTkLabel(
            body,
            text="",
            font=theme.font(12, slant="italic"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=self.WIDTH - 48,
        )
        self.message_label.grid(row=5, column=0, sticky="ew", pady=(16, 0))

        self._initial_focus = self.name_entry

    def _submit(self) -> None:
        try:
            user = self.store.add_user(self.name_entry.get())
        except StoreError as exc:
            self._show_message(str(exc), error=True)
            self.name_entry.focus_set()
            return

        try:
            self.store.save()
        except OSError as exc:
            self.store.remove_user(user.user_id)
            self._show_message(f"Erreur de sauvegarde : {exc}", error=True)
            self.name_entry.focus_set()
            return

        self.name_entry.delete(0, "end")
        self._show_message(
            f"Utilisateur ajouté : {user.name} ({user.user_id})."
        )
        self.on_saved(user)
        self.name_entry.focus_set()

    def _show_message(self, text: str, error: bool = False) -> None:
        self.message_label.configure(
            text=text,
            text_color=theme.TERRACOTTA if error else theme.SAGE,
        )
