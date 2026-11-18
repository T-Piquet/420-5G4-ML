from tkinter import ttk

import customtkinter as ctk

from theme import (
    COULEUR_BORDURE,
    COULEUR_ERREUR,
    COULEUR_FOND,
    COULEUR_FOOTER,
    COULEUR_PRIMAIRE,
    COULEUR_PRIMAIRE_SURVOL,
    COULEUR_SIDEBAR,
    COULEUR_TEXTE,
    COULEUR_TEXTE_PLACEHOLDER,
    COULEUR_TEXTE_SECONDAIRE,
    HAUTEUR_BOUTON,
    HAUTEUR_CHAMP,
    HAUTEUR_PIED,
    POLICE_BOUTON,
    POLICE_NORMALE,
    POLICE_PANNEAU,
    POLICE_PETITE,
    POLICE_TITRE,
    RAYON,
    STYLE_TABLEAU,
)

COLONNES = (
    ("nom", "Nom", 250, 150),
    ("id", "ID", 140, 100),
    ("livres", "Livres empruntés", 140, 120),
)


class EcranUtilisateurs(ctk.CTkFrame):
    def __init__(
        self,
        parent: ctk.CTkFrame,
        bibliotheque=None,
        erreur: str | None = None,
        on_mutation=None,
    ) -> None:
        super().__init__(parent, fg_color=COULEUR_FOND, corner_radius=0)
        self.bibliotheque = bibliotheque
        self.erreur = erreur
        self.on_mutation = on_mutation
        self._construire_pied()
        self._construire_contenu()
        self._rafraichir_tableau()

    def _construire_pied(self) -> None:
        pied = ctk.CTkFrame(
            self,
            height=HAUTEUR_PIED,
            fg_color=COULEUR_FOOTER,
            corner_radius=0,
        )
        pied.pack(side="bottom", fill="x")
        pied.pack_propagate(False)

        self.label_compteur = ctk.CTkLabel(
            pied,
            text="0 utilisateur",
            height=HAUTEUR_PIED,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        self.label_compteur.pack(side="left", padx=14)

    def _construire_contenu(self) -> None:
        contenu = ctk.CTkFrame(self, fg_color=COULEUR_FOND, corner_radius=0)
        contenu.pack(fill="both", expand=True, padx=24, pady=20)

        titre = ctk.CTkLabel(
            contenu,
            text="Liste des utilisateurs",
            height=24,
            font=POLICE_TITRE,
            text_color=COULEUR_TEXTE,
            anchor="w",
        )
        titre.pack(fill="x")

        corps = ctk.CTkFrame(contenu, fg_color="transparent")
        corps.pack(fill="both", expand=True, pady=(12, 0))
        corps.grid_columnconfigure(0, weight=1)
        corps.grid_columnconfigure(1, weight=0, minsize=280)
        corps.grid_rowconfigure(0, weight=1)

        self._construire_tableau(corps)
        self._construire_panneau(corps)

    def _construire_tableau(self, parent: ctk.CTkFrame) -> None:
        cadre_tableau = ctk.CTkFrame(
            parent,
            fg_color=COULEUR_FOND,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
        )
        cadre_tableau.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self.tableau = ttk.Treeview(
            cadre_tableau,
            style=STYLE_TABLEAU,
            columns=[colonne[0] for colonne in COLONNES],
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.tableau.pack(fill="both", expand=True, padx=1, pady=1)

        for cle, titre, largeur, largeur_min in COLONNES:
            self.tableau.heading(cle, text=titre, anchor="w")
            self.tableau.column(
                cle,
                width=largeur,
                minwidth=largeur_min,
                anchor="w",
                stretch=True,
            )

    def _construire_panneau(self, parent: ctk.CTkFrame) -> None:
        panneau = ctk.CTkFrame(
            parent,
            width=280,
            fg_color=COULEUR_FOND,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
        )
        panneau.grid(row=0, column=1, sticky="new")

        titre = ctk.CTkLabel(
            panneau,
            text="Ajouter un utilisateur",
            height=22,
            font=POLICE_PANNEAU,
            text_color=COULEUR_TEXTE,
            anchor="w",
        )
        titre.pack(fill="x", padx=16, pady=(16, 12))

        label_nom = ctk.CTkLabel(
            panneau,
            text="Nom",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        label_nom.pack(fill="x", padx=16, pady=(0, 4))

        self.champ_nom = ctk.CTkEntry(
            panneau,
            height=HAUTEUR_CHAMP,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
            fg_color=COULEUR_FOND,
            text_color=COULEUR_TEXTE,
            font=POLICE_NORMALE,
        )
        self.champ_nom.pack(fill="x", padx=16, pady=(0, 12))

        label_id = ctk.CTkLabel(
            panneau,
            text="ID utilisateur",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        label_id.pack(fill="x", padx=16, pady=(0, 4))

        self.champ_id = ctk.CTkEntry(
            panneau,
            height=HAUTEUR_CHAMP,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
            fg_color=COULEUR_SIDEBAR,
            text_color=COULEUR_TEXTE,
            placeholder_text="USR—",
            placeholder_text_color=COULEUR_TEXTE_PLACEHOLDER,
            font=POLICE_NORMALE,
            state="disabled",
        )
        self.champ_id.pack(fill="x", padx=16, pady=(0, 16))

        bouton = ctk.CTkButton(
            panneau,
            text="Ajouter",
            command=self._ajouter_utilisateur,
            height=HAUTEUR_BOUTON,
            corner_radius=RAYON,
            fg_color=COULEUR_PRIMAIRE,
            hover_color=COULEUR_PRIMAIRE_SURVOL,
            text_color="#ffffff",
            font=POLICE_BOUTON,
        )
        bouton.pack(fill="x", padx=16, pady=(0, 8))

        self.label_message = ctk.CTkLabel(
            panneau,
            text="",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        self.label_message.pack(fill="x", padx=16, pady=(0, 16))

    def _rafraichir_tableau(self) -> None:
        for element in self.tableau.get_children():
            self.tableau.delete(element)

        utilisateurs = (
            self.bibliotheque.all_users() if self.bibliotheque is not None else []
        )
        for utilisateur in utilisateurs:
            self.tableau.insert(
                "",
                "end",
                values=(
                    utilisateur.name,
                    utilisateur.user_id,
                    len(utilisateur.borrowed_books),
                ),
            )

        nombre = len(utilisateurs)
        libelle = "utilisateur" if nombre <= 1 else "utilisateurs"
        self.label_compteur.configure(text=f"{nombre} {libelle}")
        self._mettre_a_jour_id()

    def _mettre_a_jour_id(self) -> None:
        identifiant = self._prochain_id()
        self.champ_id.configure(state="normal")
        self.champ_id.delete(0, "end")
        if identifiant:
            self.champ_id.insert(0, identifiant)
        self.champ_id.configure(state="disabled")

    def _prochain_id(self) -> str:
        if self.bibliotheque is None:
            return ""

        existants = {utilisateur.user_id for utilisateur in self.bibliotheque.all_users()}
        numero = 1
        while f"USR{numero:03d}" in existants:
            numero += 1
        return f"USR{numero:03d}"

    def _ajouter_utilisateur(self) -> None:
        self._effacer_message()

        if self.bibliotheque is None:
            self._afficher_message("La bibliothèque n'est pas chargée.", erreur=True)
            return

        nom = self.champ_nom.get().strip()
        if not nom:
            self._afficher_message("Le nom est obligatoire.", erreur=True)
            return

        identifiant = self.champ_id.get().strip()
        if not identifiant:
            self._afficher_message("ID utilisateur indisponible.", erreur=True)
            return

        if not self.bibliotheque.add_user(nom, identifiant):
            self._afficher_message("Un utilisateur avec cet ID existe déjà.", erreur=True)
            self._mettre_a_jour_id()
            return

        self.champ_nom.delete(0, "end")
        self._rafraichir_tableau()
        if self.on_mutation is not None:
            self.on_mutation()
        self._afficher_message("Utilisateur ajouté.")

    def _afficher_message(self, message: str, erreur: bool = False) -> None:
        self.label_message.configure(
            text=message,
            text_color=COULEUR_ERREUR if erreur else COULEUR_TEXTE_SECONDAIRE,
        )

    def _effacer_message(self) -> None:
        self.label_message.configure(text="")
