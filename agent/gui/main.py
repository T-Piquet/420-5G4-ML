"""Interface graphique du système de gestion de bibliothèque personnelle."""

import argparse
import ctypes
import os
import queue
import sys
import threading
from pathlib import Path

import customtkinter as ctk

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "build"))

try:
    import bibliotheque_core as core
except ImportError as exc:
    print(
        "Erreur : impossible d'importer le module bibliotheque_core.\n"
        "Compilez d'abord le projet : cmake -S agent -B agent/build "
        "&& cmake --build agent/build",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

MENU_GROUPS = [
    (
        "Livres",
        [
            (1, "Ajouter un Livre"),
            (2, "Supprimer un Livre"),
            (3, "Rechercher des Livres par Titre"),
            (4, "Rechercher des Livres par Auteur"),
            (5, "Afficher Tous les Livres"),
            (6, "Afficher les Livres Disponibles"),
        ],
    ),
    (
        "Utilisateurs",
        [
            (7, "Ajouter un Utilisateur"),
            (8, "Afficher Tous les Utilisateurs"),
        ],
    ),
    (
        "Opérations",
        [
            (9, "Emprunter un Livre"),
            (10, "Retourner un Livre"),
        ],
    ),
    (
        "Système",
        [
            (11, "Statistiques de la Bibliothèque"),
            (12, "Sauvegarder les Données"),
            (13, "Créer une Sauvegarde"),
        ],
    ),
]

_libc = ctypes.CDLL(None)


class JournalCpp:
    """Capture la sortie standard du processus, y compris les messages C++."""

    def __init__(self):
        self._lines: "queue.Queue[str]" = queue.Queue()
        self._original_fd = os.dup(1)
        sys.stdout.flush()
        read_fd, write_fd = os.pipe()
        os.dup2(write_fd, 1)
        os.close(write_fd)
        self._reader = threading.Thread(target=self._read, args=(read_fd,), daemon=True)
        self._reader.start()

    def _read(self, read_fd):
        with os.fdopen(read_fd, "r", encoding="utf-8", errors="replace") as stream:
            for line in stream:
                self._lines.put(line.rstrip("\n"))

    @staticmethod
    def flush():
        sys.stdout.flush()
        _libc.fflush(None)

    def drain(self):
        lines = []
        while True:
            try:
                lines.append(self._lines.get_nowait())
            except queue.Empty:
                break
        return lines

    def restore(self):
        sys.stdout.flush()
        try:
            os.dup2(self._original_fd, 1)
        finally:
            os.close(self._original_fd)


class LibraryApp(ctk.CTk):
    def __init__(self, data_dir):
        super().__init__()

        self.data_dir = Path(data_dir)
        self.title("Système de Gestion de Bibliothèque Personnelle")
        self.geometry("1000x650")
        self.minsize(900, 600)

        self.journal_cpp = JournalCpp()
        self.library = core.Library()
        self.file_manager = core.FileManager(
            str(self.data_dir / "books.txt"),
            str(self.data_dir / "users.txt"),
        )

        self._poll_id = None
        self._build_layout()
        self._load_data()

        self._poll_id = self.after(100, self._poll_journal)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")

        ctk.CTkLabel(
            sidebar,
            text="Bibliothèque",
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(fill="x", padx=12, pady=(16, 8))

        for group, items in MENU_GROUPS:
            ctk.CTkLabel(
                sidebar,
                text=group,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
            ).pack(fill="x", padx=12, pady=(12, 4))
            for number, label in items:
                ctk.CTkButton(
                    sidebar,
                    text=f"{number}. {label}",
                    anchor="w",
                    state="disabled",
                ).pack(fill="x", padx=10, pady=2)

        content = ctk.CTkFrame(self, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="Journal",
            anchor="w",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        self.journal = ctk.CTkTextbox(content, wrap="word", state="disabled")
        self.journal.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        self.status = ctk.CTkLabel(self, text="Chargement…", anchor="w", height=28)
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12)

    def _load_data(self):
        print(f"Chargement des données depuis {self.data_dir}…")
        JournalCpp.flush()
        self.file_manager.loadLibraryData(self.library)
        JournalCpp.flush()
        self._refresh_status()

    def _refresh_status(self):
        total = self.library.getTotalBooks()
        disponibles = self.library.getAvailableBookCount()
        empruntes = self.library.getCheckedOutBookCount()
        utilisateurs = len(self.library.getAllUsers())
        self.status.configure(
            text=(
                f"{total} livres · {disponibles} disponibles · "
                f"{empruntes} empruntés · {utilisateurs} utilisateurs"
            )
        )

    def _append_journal(self, line):
        self.journal.configure(state="normal")
        self.journal.insert("end", line + "\n")
        self.journal.see("end")
        self.journal.configure(state="disabled")

    def _poll_journal(self):
        for line in self.journal_cpp.drain():
            self._append_journal(line)
        self._poll_id = self.after(100, self._poll_journal)

    def _on_close(self):
        if self._poll_id is not None:
            self.after_cancel(self._poll_id)
            self._poll_id = None
        JournalCpp.flush()
        for line in self.journal_cpp.drain():
            self._append_journal(line)
        self.journal_cpp.restore()
        self.destroy()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interface graphique du système de gestion de bibliothèque personnelle."
    )
    parser.add_argument(
        "-d",
        "--data-dir",
        default=str(BASE_DIR / "data"),
        help="répertoire des fichiers books.txt et users.txt (défaut : agent/data)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = Path(args.data_dir).expanduser()

    if not data_dir.is_dir():
        print(f"Erreur : le répertoire {data_dir} n'existe pas.", file=sys.stderr)
        return 1

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = LibraryApp(data_dir)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
