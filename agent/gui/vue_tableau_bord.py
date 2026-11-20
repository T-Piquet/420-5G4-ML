import customtkinter as ctk

from gui.controleur import ControleurBibliotheque


class VueTableauBord(ctk.CTkFrame):
    def __init__(self, parent, controleur: ControleurBibliotheque, sur_statut):
        super().__init__(parent, fg_color="transparent")
        self.controleur = controleur
        self.sur_statut = sur_statut
        self.labels_valeurs: dict[str, ctk.CTkLabel] = {}
        self._version_affichee = -1

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Tableau de bord",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            self,
            text=f"Répertoire de données : {self.controleur.repertoire_donnees}",
            text_color="gray",
        ).grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        grille_stats = ctk.CTkFrame(self, fg_color="transparent")
        grille_stats.grid(row=2, column=0, padx=12, pady=8, sticky="ew")
        for col in range(4):
            grille_stats.grid_columnconfigure(col, weight=1)

        cartes = [
            ("total_livres", "Total des livres", ("#1f538d", "#4a90e2")),
            ("disponibles", "Disponibles", ("#1b5e20", "#66bb6a")),
            ("empruntes", "Empruntés", ("#e65100", "#ffa726")),
            ("total_utilisateurs", "Utilisateurs", ("#4a148c", "#ab47bc")),
        ]

        for col, (cle, titre, couleur) in enumerate(cartes):
            carte = ctk.CTkFrame(grille_stats, corner_radius=12)
            carte.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")

            ctk.CTkLabel(
                carte,
                text=titre,
                font=ctk.CTkFont(size=14),
                text_color="gray",
            ).pack(anchor="w", padx=16, pady=(16, 4))

            label_valeur = ctk.CTkLabel(
                carte,
                text="0",
                font=ctk.CTkFont(size=34, weight="bold"),
                text_color=couleur,
            )
            label_valeur.pack(anchor="w", padx=16, pady=(0, 16))
            self.labels_valeurs[cle] = label_valeur

        cadre_actions = ctk.CTkFrame(self, corner_radius=12)
        cadre_actions.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        ctk.CTkLabel(
            cadre_actions,
            text="Actions de persistance",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(16, 12))

        ligne_boutons = ctk.CTkFrame(cadre_actions, fg_color="transparent")
        ligne_boutons.pack(anchor="w", padx=16, pady=(0, 16))

        ctk.CTkButton(
            ligne_boutons,
            text="Sauvegarder les données",
            height=38,
            command=self._sauvegarder,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            ligne_boutons,
            text="Créer une sauvegarde (.backup)",
            height=38,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            command=self._creer_sauvegarde,
        ).pack(side="left")

    def rafraichir(self):
        if self._version_affichee == self.controleur.version_donnees:
            return
        self._version_affichee = self.controleur.version_donnees
        stats = self.controleur.obtenir_statistiques()
        for cle, label in self.labels_valeurs.items():
            label.configure(text=str(stats.get(cle, 0)))

    def _sauvegarder(self):
        ok, message = self.controleur.sauvegarder()
        self.sur_statut(message, ok)

    def _creer_sauvegarde(self):
        ok, message = self.controleur.creer_sauvegarde()
        self.sur_statut(message, ok)
