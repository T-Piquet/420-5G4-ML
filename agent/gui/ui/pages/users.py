"""Users management page connected to BibliothequeAPI."""

import customtkinter as ctk

from theme import COLORS, FONTS, RADIUS
from ui.icons import ICON_ADD, ICON_SEARCH
from ui.pages.base import BasePage
from ui.table import ScrollableList
from ui.widgets import ItemRowCard


class AddUserDialog(ctk.CTkToplevel):
    """Modal dialog to add a new library user."""

    def __init__(self, master, on_submit) -> None:
        super().__init__(master)
        self.title("Ajouter un membre")
        self.geometry("340x210")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_submit = on_submit

        self.grid_columnconfigure(0, weight=1)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nom complet")
        self.name_entry.grid(row=0, column=0, padx=20, pady=(20, 8), sticky="ew")

        self.id_entry = ctk.CTkEntry(self, placeholder_text="ID utilisateur (ex: U001)")
        self.id_entry.grid(row=1, column=0, padx=20, pady=8, sticky="ew")

        self.error_label = ctk.CTkLabel(self, text="", text_color=COLORS["danger"], font=FONTS["small"])
        self.error_label.grid(row=2, column=0, padx=20, pady=4, sticky="w")

        ctk.CTkButton(self, text="Ajouter", command=self._submit).grid(
            row=3, column=0, padx=20, pady=(8, 16), sticky="e"
        )

    def _submit(self) -> None:
        ok, msg = self._on_submit(self.name_entry.get(), self.id_entry.get())
        if ok:
            self.destroy()
        else:
            self.error_label.configure(text=msg)


class EditUserDialog(ctk.CTkToplevel):
    """Modal dialog to rename an existing user."""

    def __init__(self, master, current_name: str, on_submit) -> None:
        super().__init__(master)
        self.title("Modifier le membre")
        self.geometry("340x170")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._on_submit = on_submit

        self.grid_columnconfigure(0, weight=1)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nom complet")
        self.name_entry.insert(0, current_name)
        self.name_entry.grid(row=0, column=0, padx=20, pady=(20, 8), sticky="ew")

        self.error_label = ctk.CTkLabel(self, text="", text_color=COLORS["danger"], font=FONTS["small"])
        self.error_label.grid(row=1, column=0, padx=20, pady=4, sticky="w")

        ctk.CTkButton(self, text="Enregistrer", command=self._submit).grid(
            row=2, column=0, padx=20, pady=(8, 16), sticky="e"
        )

    def _submit(self) -> None:
        ok, msg = self._on_submit(self.name_entry.get())
        if ok:
            self.destroy()
        else:
            self.error_label.configure(text=msg)


class UsersPage(BasePage):
    """Displays library members with search, add, and edit actions."""

    def __init__(self, master, api) -> None:
        super().__init__(master, api)
        self.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")

        ctk.CTkLabel(
            toolbar,
            text="ID",
            font=FONTS["body"],
            text_color=COLORS["text_light"],
        ).grid(row=0, column=0, padx=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text=ICON_SEARCH,
            width=200,
            height=34,
            corner_radius=RADIUS["input"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_width=0,
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 14))
        self.search_var.trace_add("write", lambda *_: self.refresh())

        self.add_btn = ctk.CTkButton(
            toolbar,
            text=ICON_ADD,
            width=110,
            height=34,
            corner_radius=RADIUS["button"],
            fg_color=COLORS["bg_button"],
            hover_color=COLORS["bg_button_hover"],
            text_color=COLORS["text_primary"],
            font=FONTS["body"],
            command=self._on_add_clicked,
        )
        self.add_btn.grid(row=0, column=2, padx=(0, 8))

        self.list_frame = ScrollableList(self)
        self.list_frame.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="nsew")

        self.feedback_label = ctk.CTkLabel(
            self, text="", font=FONTS["small"], text_color=COLORS["text_light"], anchor="w"
        )
        self.feedback_label.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")

    def refresh(self) -> None:
        self.list_frame.clear()
        query = self.search_var.get().strip().lower()

        for user in self.api.get_all_users():
            if query and query not in user.user_id.lower() and query not in user.name.lower():
                continue
            count = len(user.borrowed_books)
            text = f"{user.name} ({user.user_id}) — {count} livre(s) emprunté(s)"
            row = ItemRowCard(
                self.list_frame,
                text=text,
                on_edit=lambda uid=user.user_id, uname=user.name: self._on_edit_clicked(uid, uname),
            )
            self.list_frame.add_row(row)

    def _on_add_clicked(self) -> None:
        def submit(name: str, user_id: str):
            ok, msg = self.api.add_user(name, user_id)
            if ok:
                self.feedback_label.configure(text=msg)
                self.refresh()
            return ok, msg

        AddUserDialog(self, submit)

    def _on_edit_clicked(self, user_id: str, current_name: str) -> None:
        def submit(new_name: str):
            ok, msg = self.api.update_user_name(user_id, new_name)
            if ok:
                self.feedback_label.configure(text=msg)
                self.refresh()
            return ok, msg

        EditUserDialog(self, current_name, submit)
