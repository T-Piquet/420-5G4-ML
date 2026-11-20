import customtkinter as ctk

from gui.controleur import ControleurBibliotheque


class VueUtilisateurs(ctk.CTkFrame):
    def __init__(self, parent, controleur: ControleurBibliotheque, sur_statut):
        super().__init__(parent, fg_color="transparent")
        self.controleur = controleur
        self.sur_statut = sur_statut

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, padx=16, pady=(12, 8), sticky="ew")
        entete.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            entete,
            text="Gestion des utilisateurs",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.label_compteur = ctk.CTkLabel(entete, text="", text_color="gray")
        self.label_compteur.grid(row=0, column=1, sticky="e")

        cadre_ajout = ctk.CTkFrame(self, corner_radius=10)
        cadre_ajout.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        cadre_ajout.grid_columnconfigure(0, weight=2)
        cadre_ajout.grid_columnconfigure(1, weight=1)

        self.entree_nom = ctk.CTkEntry(cadre_ajout, placeholder_text="Nom complet")
        self.entree_nom.grid(row=0, column=0, padx=(12, 6), pady=10, sticky="ew")

        self.entree_id = ctk.CTkEntry(
            cadre_ajout,
            placeholder_text="ID utilisateur (ex. USR026)",
        )
        self.entree_id.grid(row=0, column=1, padx=6, pady=10, sticky="ew")

        ctk.CTkButton(
            cadre_ajout,
            text="Ajouter",
            width=110,
            command=self._ajouter_utilisateur,
        ).grid(row=0, column=2, padx=(6, 12), pady=10)

        self.liste_utilisateurs = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.liste_utilisateurs.grid(row=2, column=0, padx=16, pady=(6, 12), sticky="nsew")
        self.liste_utilisateurs.grid_columnconfigure(0, weight=1)

    def _ajouter_utilisateur(self):
        ok, message = self.controleur.ajouter_utilisateur(
            self.entree_nom.get(),
            self.entree_id.get(),
        )
        self.sur_statut(message, ok)
        if ok:
            self.entree_nom.delete(0, "end")
            self.entree_id.delete(0, "end")
            self.rafraichir()

    def rafraichir(self):
        for widget in self.liste_utilisateurs.winfo_children():
            widget.destroy()

        utilisateurs = self.controleur.obtenir_tous_les_utilisateurs()
        self.label_compteur.configure(text=f"{len(utilisateurs)} utilisateur(s)")

        if not utilisateurs:
            ctk.CTkLabel(
                self.liste_utilisateurs,
                text="Aucun utilisateur enregistré.",
                text_color="gray",
            ).grid(row=0, column=0, pady=24)
            return

        for index, utilisateur in enumerate(utilisateurs):
            ligne = ctk.CTkFrame(self.liste_utilisateurs, corner_radius=8)
            ligne.grid(row=index, column=0, padx=6, pady=4, sticky="ew")
            ligne.grid_columnconfigure(0, weight=1)

            info = ctk.CTkFrame(ligne, fg_color="transparent")
            info.grid(row=0, column=0, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(
                info,
                text=f"{utilisateur.get_name()}  ({utilisateur.get_user_id()})",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(anchor="w")

            emprunts = utilisateur.get_borrowed_books()
            if emprunts:
                details = []
                for isbn in emprunts:
                    livre = self.controleur.bibliotheque.find_book_by_isbn(isbn)
                    details.append(f"{livre.get_title()} ({isbn})" if livre else isbn)
                texte_emprunts = "Emprunts : " + ", ".join(details)
            else:
                texte_emprunts = "Aucun livre emprunté"

            ctk.CTkLabel(
                info,
                text=texte_emprunts,
                font=ctk.CTkFont(size=12),
                text_color="gray",
            ).pack(anchor="w")

            nb = utilisateur.get_number_of_borrowed_books()
            ctk.CTkLabel(
                ligne,
                text=f"{nb} emprunt(s)",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#e65100", "#ffa726") if nb > 0 else "gray",
            ).grid(row=0, column=1, padx=14, pady=8)
