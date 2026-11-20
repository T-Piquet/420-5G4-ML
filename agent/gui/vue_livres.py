import customtkinter as ctk

from gui.controleur import ControleurBibliotheque


class VueLivres(ctk.CTkFrame):
    def __init__(self, parent, controleur: ControleurBibliotheque, sur_statut):
        super().__init__(parent, fg_color="transparent")
        self.controleur = controleur
        self.sur_statut = sur_statut

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, padx=16, pady=(12, 8), sticky="ew")
        entete.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            entete,
            text="Gestion des livres",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.label_compteur = ctk.CTkLabel(entete, text="", text_color="gray")
        self.label_compteur.grid(row=0, column=1, sticky="e")

        barre_recherche = ctk.CTkFrame(self, corner_radius=10)
        barre_recherche.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        barre_recherche.grid_columnconfigure(0, weight=1)

        self.entree_recherche = ctk.CTkEntry(
            barre_recherche,
            placeholder_text="Rechercher un livre...",
        )
        self.entree_recherche.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="ew")
        self.entree_recherche.bind("<Return>", lambda _e: self.rafraichir())

        self.critere_recherche = ctk.CTkOptionMenu(
            barre_recherche,
            values=["Titre", "Auteur"],
            width=110,
        )
        self.critere_recherche.grid(row=0, column=1, padx=4, pady=10)

        ctk.CTkButton(
            barre_recherche,
            text="Rechercher",
            width=100,
            command=self.rafraichir,
        ).grid(row=0, column=2, padx=4, pady=10)

        ctk.CTkButton(
            barre_recherche,
            text="Réinitialiser",
            width=100,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._reinitialiser_recherche,
        ).grid(row=0, column=3, padx=4, pady=10)

        self.filtre_statut = ctk.CTkSegmentedButton(
            barre_recherche,
            values=["Tous", "Disponibles"],
            command=lambda _v: self.rafraichir(),
        )
        self.filtre_statut.set("Tous")
        self.filtre_statut.grid(row=0, column=4, padx=(8, 12), pady=10)

        cadre_ajout = ctk.CTkFrame(self, corner_radius=10)
        cadre_ajout.grid(row=2, column=0, padx=16, pady=6, sticky="ew")
        for col in range(3):
            cadre_ajout.grid_columnconfigure(col, weight=1)

        self.entree_titre = ctk.CTkEntry(cadre_ajout, placeholder_text="Titre du livre")
        self.entree_titre.grid(row=0, column=0, padx=(12, 6), pady=10, sticky="ew")

        self.entree_auteur = ctk.CTkEntry(cadre_ajout, placeholder_text="Auteur")
        self.entree_auteur.grid(row=0, column=1, padx=6, pady=10, sticky="ew")

        self.entree_isbn = ctk.CTkEntry(cadre_ajout, placeholder_text="ISBN")
        self.entree_isbn.grid(row=0, column=2, padx=6, pady=10, sticky="ew")

        ctk.CTkButton(
            cadre_ajout,
            text="Ajouter",
            width=110,
            command=self._ajouter_livre,
        ).grid(row=0, column=3, padx=(6, 12), pady=10)

        self.liste_livres = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.liste_livres.grid(row=3, column=0, padx=16, pady=(6, 12), sticky="nsew")
        self.liste_livres.grid_columnconfigure(0, weight=1)

    def _reinitialiser_recherche(self):
        self.entree_recherche.delete(0, "end")
        self.filtre_statut.set("Tous")
        self.rafraichir()

    def _ajouter_livre(self):
        ok, message = self.controleur.ajouter_livre(
            self.entree_titre.get(),
            self.entree_auteur.get(),
            self.entree_isbn.get(),
        )
        self.sur_statut(message, ok)
        if ok:
            self.entree_titre.delete(0, "end")
            self.entree_auteur.delete(0, "end")
            self.entree_isbn.delete(0, "end")
            self.rafraichir()

    def _supprimer_livre(self, isbn: str):
        ok, message = self.controleur.supprimer_livre(isbn)
        self.sur_statut(message, ok)
        if ok:
            self.rafraichir()

    def _obtenir_livres_filtres(self):
        terme = self.entree_recherche.get().strip()
        if terme:
            if self.critere_recherche.get() == "Auteur":
                livres = self.controleur.rechercher_livres_par_auteur(terme)
            else:
                livres = self.controleur.rechercher_livres_par_titre(terme)
        else:
            livres = self.controleur.obtenir_tous_les_livres()

        if self.filtre_statut.get() == "Disponibles":
            livres = [livre for livre in livres if livre.is_available()]

        return livres

    def rafraichir(self):
        for widget in self.liste_livres.winfo_children():
            widget.destroy()

        livres = self._obtenir_livres_filtres()
        self.label_compteur.configure(text=f"{len(livres)} livre(s) affiché(s)")

        if not livres:
            ctk.CTkLabel(
                self.liste_livres,
                text="Aucun livre ne correspond aux critères.",
                text_color="gray",
            ).grid(row=0, column=0, pady=24)
            return

        for index, livre in enumerate(livres):
            ligne = ctk.CTkFrame(self.liste_livres, corner_radius=8)
            ligne.grid(row=index, column=0, padx=6, pady=4, sticky="ew")
            ligne.grid_columnconfigure(0, weight=1)

            info = ctk.CTkFrame(ligne, fg_color="transparent")
            info.grid(row=0, column=0, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(
                info,
                text=livre.get_title(),
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=f"{livre.get_author()}  •  ISBN : {livre.get_isbn()}",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(anchor="w")

            disponible = livre.is_available()
            texte_statut = (
                "Disponible"
                if disponible
                else f"Emprunté ({livre.get_borrower_id()})"
            )
            couleur_statut = ("#1b5e20", "#66bb6a") if disponible else ("#e65100", "#ffa726")

            ctk.CTkLabel(
                ligne,
                text=texte_statut,
                text_color=couleur_statut,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=1, padx=12, pady=8)

            ctk.CTkButton(
                ligne,
                text="Supprimer",
                width=92,
                height=30,
                fg_color=("#c62828", "#b71c1c") if disponible else "gray50",
                hover_color=("#8e0000", "#7f0000"),
                state="normal" if disponible else "disabled",
                command=lambda isbn=livre.get_isbn(): self._supprimer_livre(isbn),
            ).grid(row=0, column=2, padx=(4, 12), pady=8)
