import argparse
import sys
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from . import theme
from .books_view import BooksView
from .settings_view import SettingsView
from .users_view import UsersView
from .widgets import NavBar

RACINE_PROJET = Path(__file__).resolve().parent.parent
REPERTOIRE_BUILD = RACINE_PROJET / "build"


def charger_module():
    try:
        import bibliotheque
    except ImportError:
        if REPERTOIRE_BUILD.is_dir():
            sys.path.insert(0, str(REPERTOIRE_BUILD))
        try:
            import bibliotheque
        except ImportError as exc:
            raise SystemExit(
                "Le module Python « bibliotheque » est introuvable.\n"
                "Compilez d'abord le projet depuis agent/ :\n"
                "  cmake -S . -B build && cmake --build build -j"
            ) from exc
    return bibliotheque


class FenetrePrincipale(ctk.CTk):
    def __init__(self, module, repertoire_donnees):
        super().__init__()
        self.module = module
        self.library = module.Library()
        self.file_manager = module.FileManager(
            str(repertoire_donnees / "books.txt"),
            str(repertoire_donnees / "users.txt"),
        )
        self.file_manager.loadLibraryData(self.library)

        self.title("Bibliothèque")
        self.geometry("960x580")
        self.minsize(780, 500)
        self.configure(fg_color=theme.FOND)
        self.protocol("WM_DELETE_WINDOW", self.quitter)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.contenu = ctk.CTkFrame(self, fg_color="transparent")
        self.contenu.grid(row=0, column=0, sticky="nsew")
        self.contenu.grid_rowconfigure(0, weight=1)
        self.contenu.grid_columnconfigure(0, weight=1)

        self.vues = {
            "livres": BooksView(
                self.contenu,
                self.library,
                module.Book,
                sur_modification_utilisateurs=self.rafraichir_utilisateurs,
            ),
            "utilisateurs": UsersView(self.contenu, self.library, module.User),
            "parametres": SettingsView(
                self.contenu,
                self.library,
                self.sauvegarder_avec_confirmation,
                self.creer_sauvegarde,
            ),
        }

        self.nav = NavBar(self, self.afficher_vue)
        self.nav.grid(row=1, column=0, sticky="ew")

        self.afficher_vue("livres")

    def afficher_vue(self, nom):
        for vue in self.vues.values():
            vue.grid_forget()
        self.vues[nom].grid(row=0, column=0, sticky="nsew")
        self.nav.activer(nom)

    def rafraichir_utilisateurs(self):
        vue = getattr(self, "vues", {}).get("utilisateurs")
        if vue is not None:
            vue.rafraichir()

    def sauvegarder(self):
        try:
            return self.file_manager.saveLibraryData(self.library)
        except Exception as exc:
            messagebox.showerror(
                "Erreur de sauvegarde",
                f"Impossible d'enregistrer les données.\n\n{exc}",
                parent=self,
            )
            return False

    def sauvegarder_avec_confirmation(self):
        if self.sauvegarder():
            messagebox.showinfo(
                "Sauvegarde",
                "Les données de la bibliothèque ont été sauvegardées.",
                parent=self,
            )

    def creer_sauvegarde(self):
        if not self.sauvegarder():
            return

        try:
            succes = self.file_manager.createBackup()
        except Exception as exc:
            messagebox.showerror(
                "Créer une sauvegarde",
                f"Impossible de créer la sauvegarde.\n\n{exc}",
                parent=self,
            )
            return

        if not succes:
            messagebox.showerror(
                "Créer une sauvegarde",
                "Impossible de créer les fichiers de sauvegarde.",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Créer une sauvegarde",
            "Les données ont été sauvegardées puis copiées dans "
            "books.txt.backup et users.txt.backup.",
            parent=self,
        )

    def quitter(self):
        if not self.sauvegarder():
            if not messagebox.askyesno(
                "Quitter",
                "La sauvegarde a échoué. Fermer la fenêtre quand même ?",
                parent=self,
            ):
                return
        self.quit()


def analyser_arguments():
    analyseur = argparse.ArgumentParser(
        description="Interface graphique de gestion de bibliothèque."
    )
    analyseur.add_argument(
        "-d",
        "--data-dir",
        default=str(RACINE_PROJET / "data"),
        help="répertoire contenant books.txt et users.txt (défaut : agent/data)",
    )
    return analyseur.parse_args()


def main():
    arguments = analyser_arguments()
    repertoire = Path(arguments.data_dir).expanduser().resolve()

    if not repertoire.is_dir():
        raise SystemExit(
            f"Erreur : le répertoire de données « {repertoire} » n'existe pas."
        )

    module = charger_module()
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    fenetre = FenetrePrincipale(module, repertoire)
    fenetre.mainloop()
