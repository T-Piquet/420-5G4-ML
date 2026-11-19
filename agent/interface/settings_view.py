import tkinter as tk

import customtkinter as ctk

from . import theme
from .widgets import DialogueBase


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, library, sur_sauvegarder, sur_creer_sauvegarde):
        super().__init__(master, fg_color="transparent")
        self.library = library
        self.sur_sauvegarder = sur_sauvegarder
        self.sur_creer_sauvegarde = sur_creer_sauvegarde

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construire_entete()
        self._construire_actions()

    def _construire_entete(self):
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))
        ctk.CTkLabel(
            entete,
            text="Bibliothèque",
            font=theme.police(30),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            entete,
            text="Paramètres",
            font=theme.police(13),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(anchor="w")

    def _construire_actions(self):
        corps = tk.Frame(self, bg=theme.FOND)
        corps.grid(row=1, column=0, sticky="nsew")

        actions = (
            (
                "Sauvegarder les données",
                _dessiner_disquette,
                self.sur_sauvegarder,
            ),
            (
                "Créer une sauvegarde",
                _dessiner_document,
                self.sur_creer_sauvegarde,
            ),
            (
                "Statistiques de la bibliothèque",
                _dessiner_histogramme,
                self.afficher_statistiques,
            ),
        )

        positions = (0.22, 0.5, 0.78)
        for (texte, dessin, commande), position in zip(actions, positions):
            ActionTile(corps, texte, dessin, commande).place(
                relx=position,
                rely=0.47,
                anchor="center",
            )

    def afficher_statistiques(self):
        dialogue = DialogueStatistiques(self, self.library)
        self.wait_window(dialogue)


class ActionTile(tk.Frame):
    def __init__(self, master, texte, dessiner, commande):
        super().__init__(master, bg=theme.FOND)
        self.commande = commande

        self.canvas = tk.Canvas(
            self,
            width=100,
            height=90,
            bg=theme.FOND,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.canvas.pack()
        dessiner(self.canvas)

        self.libelle = tk.Label(
            self,
            text=texte,
            bg=theme.FOND,
            fg=theme.TEXTE,
            font=(theme.FAMILLE, 12),
            justify="center",
            wraplength=245,
            cursor="hand2",
        )
        self.libelle.pack(pady=(12, 0))

        for widget in (self.canvas, self.libelle):
            widget.bind("<Button-1>", self._clic)
            widget.bind("<Enter>", self._entrer)
            widget.bind("<Leave>", self._sortir)

    def _clic(self, _):
        self.commande()

    def _entrer(self, _):
        self.libelle.configure(font=(theme.FAMILLE, 12, "underline"))

    def _sortir(self, _):
        self.libelle.configure(font=(theme.FAMILLE, 12))


class DialogueStatistiques(DialogueBase):
    def __init__(self, master, library):
        super().__init__(master, "Statistiques de la bibliothèque", 380, 280)

        contenu = ctk.CTkFrame(self, fg_color="transparent")
        contenu.pack(fill="both", expand=True, padx=20, pady=(14, 0))
        contenu.grid_columnconfigure(1, weight=1)

        lignes = (
            ("Total des livres", library.getTotalBooks()),
            ("Livres disponibles", library.getAvailableBookCount()),
            ("Livres empruntés", library.getCheckedOutBookCount()),
            ("Total des utilisateurs", len(library.getAllUsers())),
        )

        for index, (libelle, valeur) in enumerate(lignes):
            ctk.CTkLabel(
                contenu,
                text=libelle,
                font=theme.police(13),
                text_color=theme.TEXTE_SECONDAIRE,
                anchor="w",
            ).grid(row=index, column=0, sticky="w", pady=6)
            ctk.CTkLabel(
                contenu,
                text=str(valeur),
                font=theme.police(14, "bold"),
                text_color=theme.TEXTE,
                anchor="e",
            ).grid(row=index, column=1, sticky="e", pady=6)

        ctk.CTkButton(
            self,
            text="Fermer",
            width=110,
            height=32,
            corner_radius=4,
            fg_color=theme.BOUTON,
            hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            border_width=1,
            border_color=theme.BORDURE,
            font=theme.police(12),
            command=self.destroy,
        ).pack(pady=(12, 16))

        self.bind("<Return>", lambda _: self.destroy())
        self.bind("<Escape>", lambda _: self.destroy())


def _dessiner_disquette(canvas):
    canvas.create_line(
        18,
        10,
        68,
        10,
        84,
        26,
        84,
        82,
        18,
        82,
        18,
        10,
        width=4,
        fill=theme.TEXTE,
        capstyle="round",
        joinstyle="round",
    )
    canvas.create_rectangle(28, 18, 72, 34, fill=theme.TEXTE, outline="")
    canvas.create_rectangle(58, 18, 64, 26, fill=theme.FOND, outline="")
    canvas.create_rectangle(30, 54, 72, 74, outline=theme.TEXTE, width=3)
    canvas.create_oval(43, 58, 57, 72, fill=theme.TEXTE, outline="")


def _dessiner_document(canvas):
    canvas.create_line(
        26,
        10,
        60,
        10,
        74,
        24,
        74,
        52,
        26,
        52,
        26,
        10,
        width=4,
        fill=theme.TEXTE,
        capstyle="round",
        joinstyle="round",
    )
    canvas.create_line(
        60,
        10,
        60,
        24,
        74,
        24,
        width=3,
        fill=theme.TEXTE,
        capstyle="round",
        joinstyle="round",
    )
    canvas.create_rectangle(36, 20, 64, 30, fill=theme.TEXTE, outline="")
    canvas.create_oval(38, 36, 54, 52, fill=theme.TEXTE, outline="")
    canvas.create_polygon(
        58,
        52,
        76,
        34,
        84,
        42,
        66,
        60,
        fill=theme.TEXTE,
        outline=theme.FOND,
        width=2,
    )
    canvas.create_polygon(
        58,
        52,
        66,
        60,
        50,
        66,
        fill=theme.TEXTE,
        outline=theme.FOND,
    )


def _dessiner_histogramme(canvas):
    barres = ((22, 52), (40, 36), (58, 22), (76, 8))
    for x, dessus in barres:
        canvas.create_rectangle(
            x,
            dessus,
            x + 10,
            80,
            fill=theme.TEXTE,
            outline="",
        )
