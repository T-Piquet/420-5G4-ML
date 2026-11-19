import customtkinter as ctk
from tkinter import messagebox

from . import theme
from .widgets import DialogueBase, UserCard


class UsersView(ctk.CTkFrame):
    def __init__(self, master, library, user_class):
        super().__init__(master, fg_color="transparent")
        self.library = library
        self.user_class = user_class

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construire_entete()
        self._construire_barre()
        self._construire_liste()
        self.rafraichir()

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
            text="Utilisateurs",
            font=theme.police(13),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(anchor="w")

    def _construire_barre(self):
        barre = ctk.CTkFrame(self, fg_color="transparent")
        barre.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 8))
        ctk.CTkButton(
            barre,
            text="Ajouter un utilisateur",
            width=200,
            height=32,
            corner_radius=4,
            fg_color=theme.BOUTON,
            hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            border_width=1,
            border_color=theme.BORDURE,
            font=theme.police(12),
            command=self.ajouter_utilisateur,
        ).pack(side="right")

    def _construire_liste(self):
        self.liste = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_fg_color=theme.FOND,
            scrollbar_button_color=theme.BOUTON,
            scrollbar_button_hover_color=theme.BOUTON_SURVOL,
        )
        self.liste.grid(row=2, column=0, sticky="nsew", padx=24, pady=(4, 16))

    def rafraichir(self):
        utilisateurs = list(self.library.getAllUsers())

        for enfant in self.liste.winfo_children():
            enfant.destroy()

        if not utilisateurs:
            ctk.CTkLabel(
                self.liste,
                text="Aucun utilisateur enregistré.",
                font=theme.police(14),
                text_color=theme.TEXTE_SECONDAIRE,
            ).pack(pady=48)
            return

        for utilisateur in utilisateurs:
            UserCard(self.liste, utilisateur).pack(fill="x", padx=2, pady=6)

    def ajouter_utilisateur(self):
        dialogue = DialogueAjoutUtilisateur(self, self.library)
        self.wait_window(dialogue)
        if dialogue.resultat:
            nom, identifiant = dialogue.resultat
            self.library.addUser(self.user_class(nom, identifiant))
            self.rafraichir()


class DialogueAjoutUtilisateur(DialogueBase):
    def __init__(self, master, library):
        super().__init__(master, "Ajouter un utilisateur", 380, 250)
        self.library = library

        self.entree_nom = self._champ(self, "Nom")
        self.entree_id = self._champ(self, "ID")
        self._boutons(self, "Ajouter", self.valider)

        self.entree_nom.focus_set()
        self.bind("<Return>", lambda _: self.valider())

    def valider(self):
        nom = self.entree_nom.get().strip()
        identifiant = self.entree_id.get().strip()

        if not nom or not identifiant:
            messagebox.showwarning(
                "Champs requis",
                "Le nom et l'ID sont obligatoires.",
                parent=self,
            )
            return

        if "|" in nom or "|" in identifiant:
            messagebox.showerror(
                "Caractère interdit",
                "Le caractère « | » ne peut pas être utilisé dans les champs.",
                parent=self,
            )
            return

        if self.library.findUserById(identifiant):
            messagebox.showerror(
                "ID existant",
                f"Un utilisateur avec l'ID {identifiant} existe déjà.",
                parent=self,
            )
            return

        self.resultat = (nom, identifiant)
        self.destroy()
