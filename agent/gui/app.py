#!/usr/bin/env python3
"""Point d'entree de l'interface graphique de la bibliotheque."""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk

AGENT_DIR = Path(__file__).resolve().parents[1]
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from gui.components.status_bar import StatusBar
from gui.service import LibraryService
from gui.views.catalogue_view import CatalogueView
from gui.views.dashboard_view import DashboardView
from gui.views.loans_view import LoansView
from gui.views.users_view import UsersView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BibliothequeApp(ctk.CTk):
    def __init__(self, data_dir: Path) -> None:
        super().__init__()
        self.title("Bibliothèque personnelle")
        self.geometry("1180x720")
        self.minsize(1024, 640)

        self.service = LibraryService(data_dir)
        self.current_view: str | None = None
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.views: dict[str, ctk.CTkFrame] = {}
        self.view_titles = {
            "dashboard": "Tableau de bord",
            "catalogue": "Catalogue",
            "users": "Adhérents",
            "loans": "Emprunts en cours",
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()
        self._build_status_bar()
        self._build_views()

        self.show_view("dashboard")
        self._update_status()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=("gray90", "gray13"),
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="BIBLIOTHÈQUE",
            anchor="w",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray95"),
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(24, 2))

        ctk.CTkLabel(
            sidebar,
            text="Gestion personnelle",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray60"),
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))

        ctk.CTkFrame(
            sidebar,
            height=2,
            fg_color=("gray80", "gray25"),
        ).grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 14))

        navigation = [
            ("dashboard", "Tableau de bord"),
            ("catalogue", "Catalogue"),
            ("users", "Adhérents"),
            ("loans", "Emprunts en cours"),
        ]
        for row, (key, label) in enumerate(navigation, start=3):
            button = ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                height=40,
                corner_radius=10,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                text_color=("gray20", "gray85"),
                font=ctk.CTkFont(size=14),
                command=lambda view_key=key: self.show_view(view_key),
            )
            button.grid(row=row, column=0, sticky="ew", padx=14, pady=3)
            self.nav_buttons[key] = button

        self.theme_var = tk.BooleanVar(value=True)
        self.theme_switch = ctk.CTkSwitch(
            sidebar,
            text="Mode sombre",
            variable=self.theme_var,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=13),
        )
        self.theme_switch.grid(
            row=9, column=0, sticky="w", padx=22, pady=(12, 6)
        )

        ctk.CTkLabel(
            sidebar,
            text="Jalon 3 · Lecture seule",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray55"),
        ).grid(row=10, column=0, sticky="ew", padx=22, pady=(0, 18))

    def _build_main(self) -> None:
        main = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("gray96", "gray10"),
        )
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(
            row=0, column=0, sticky="ew", padx=24, pady=(20, 10)
        )
        header.grid_columnconfigure(0, weight=1)

        self.page_title = ctk.CTkLabel(
            header,
            text="Tableau de bord",
            anchor="w",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.page_title.grid(row=0, column=0, sticky="w")

        self.refresh_button = ctk.CTkButton(
            header,
            text="Actualiser",
            width=120,
            height=36,
            command=self.refresh_current,
        )
        self.refresh_button.grid(row=0, column=1, sticky="e")

        self.content = ctk.CTkFrame(main, fg_color="transparent")
        self.content.grid(
            row=1, column=0, sticky="nsew", padx=24, pady=(0, 20)
        )
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_status_bar(self) -> None:
        self.status_bar = StatusBar(
            self,
            data_path=str(self.service.data_dir),
        )
        self.status_bar.grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )

    def _build_views(self) -> None:
        self.views = {
            "dashboard": DashboardView(self.content, self.service),
            "catalogue": CatalogueView(self.content, self.service),
            "users": UsersView(self.content, self.service),
            "loans": LoansView(self.content, self.service),
        }
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def show_view(self, key: str) -> None:
        if key not in self.views:
            return

        self.current_view = key
        self.page_title.configure(text=self.view_titles[key])
        self._set_active_nav(key)

        try:
            self.views[key].refresh()
        except Exception as exc:
            self.status_bar.set_status(
                f"Erreur d'affichage : {exc}", "error"
            )

        self.views[key].tkraise()

    def _set_active_nav(self, active_key: str) -> None:
        for key, button in self.nav_buttons.items():
            if key == active_key:
                button.configure(
                    fg_color=("gray78", "gray28"),
                    text_color=("gray10", "gray95"),
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray85"),
                )

    def _update_status(self) -> None:
        self.status_bar.set_data_path(str(self.service.data_dir))
        if self.service.load_error:
            self.status_bar.set_status(self.service.load_error, "warning")
            return

        stats = self.service.get_stats()
        self.status_bar.set_status(
            (
                f"Données chargées : {stats.total_books} livre(s), "
                f"{stats.users} adhérent(s)."
            ),
            "success",
        )

    def refresh_current(self) -> None:
        self.service.reload()
        self._update_status()
        if self.current_view is not None:
            try:
                self.views[self.current_view].refresh()
            except Exception as exc:
                self.status_bar.set_status(
                    f"Erreur d'affichage : {exc}", "error"
                )

    def _toggle_theme(self) -> None:
        ctk.set_appearance_mode(
            "dark" if self.theme_var.get() else "light"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Interface graphique de gestion de bibliothèque personnelle."
        )
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help=(
            "Répertoire contenant books.txt et users.txt "
            "(défaut : agent/data)."
        ),
    )
    return parser.parse_args()


def resolve_data_dir(value: str | None) -> Path:
    if value is None:
        return AGENT_DIR / "data"

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def main() -> int:
    args = parse_args()
    data_dir = resolve_data_dir(args.data_dir)

    try:
        app = BibliothequeApp(data_dir)
    except Exception as exc:
        print(
            f"Erreur au démarrage de l'interface : {exc}",
            file=sys.stderr,
        )
        return 1

    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
