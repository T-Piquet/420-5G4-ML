import customtkinter as ctk

from gui.controleur import ControleurBibliotheque


class VueUtilisateurs(ctk.CTkFrame):
    def __init__(self, parent, controleur: ControleurBibliotheque, sur_statut):
        super().__init__(parent, fg_color="transparent")
        self.controleur = controleur
        self.sur_statut = sur_statut

        self._version_affichee = -1
        self._lignes: list[dict] = []

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

        self._label_vide = ctk.CTkLabel(
            self.liste_utilisateurs,
            text="Aucun utilisateur enregistré.",
            text_color="gray",
        )
        self._font_nom = ctk.CTkFont(size=14, weight="bold")
        self._font_detail = ctk.CTkFont(size=12)
        self._font_badge = ctk.CTkFont(size=12, weight="bold")

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

    def _creer_ligne(self, index: int) -> dict:
        cadre = ctk.CTkFrame(self.liste_utilisateurs, corner_radius=8)
        cadre.grid_columnconfigure(0, weight=1)

        label_nom = ctk.CTkLabel(cadre, text="", font=self._font_nom, anchor="w")
        label_nom.grid(row=0, column=0, padx=(12, 8), pady=(8, 0), sticky="w")

        label_emprunts = ctk.CTkLabel(
            cadre,
            text="",
            font=self._font_detail,
            text_color="gray",
            anchor="w",
        )
        label_emprunts.grid(row=1, column=0, padx=(12, 8), pady=(0, 8), sticky="w")

        label_nb = ctk.CTkLabel(cadre, text="", font=self._font_badge)
        label_nb.grid(row=0, column=1, rowspan=2, padx=14, pady=8)

        cadre.grid(row=index, column=0, padx=6, pady=4, sticky="ew")
        return {
            "cadre": cadre,
            "nom": label_nom,
            "emprunts": label_emprunts,
            "nb": label_nb,
        }

    def rafraichir(self):
        if self._version_affichee == self.controleur.version_donnees:
            return
        self._version_affichee = self.controleur.version_donnees

        utilisateurs = self.controleur.obtenir_tous_les_utilisateurs()
        self.label_compteur.configure(text=f"{len(utilisateurs)} utilisateur(s)")

        if not utilisateurs:
            for ligne in self._lignes:
                ligne["cadre"].grid_remove()
            self._label_vide.grid(row=0, column=0, pady=24)
            return

        self._label_vide.grid_remove()

        for index, utilisateur in enumerate(utilisateurs):
            if index >= len(self._lignes):
                self._lignes.append(self._creer_ligne(index))
            else:
                self._lignes[index]["cadre"].grid(
                    row=index, column=0, padx=6, pady=4, sticky="ew"
                )

            emprunts = utilisateur.get_borrowed_books()
            if emprunts:
                details = []
                for isbn in emprunts:
                    livre = self.controleur.bibliotheque.find_book_by_isbn(isbn)
                    details.append(f"{livre.get_title()} ({isbn})" if livre else isbn)
                texte_emprunts = "Emprunts : " + ", ".join(details)
            else:
                texte_emprunts = "Aucun livre emprunté"

            nb = utilisateur.get_number_of_borrowed_books()
            ligne = self._lignes[index]
            ligne["nom"].configure(
                text=f"{utilisateur.get_name()}  ({utilisateur.get_user_id()})"
            )
            ligne["emprunts"].configure(text=texte_emprunts)
            ligne["nb"].configure(
                text=f"{nb} emprunt(s)",
                text_color=("#e65100", "#ffa726") if nb > 0 else "gray",
            )

        for index in range(len(utilisateurs), len(self._lignes)):
            self._lignes[index]["cadre"].grid_remove()
