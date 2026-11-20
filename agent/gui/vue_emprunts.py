import customtkinter as ctk

from gui.controleur import ControleurBibliotheque


class VueEmprunts(ctk.CTkFrame):
    def __init__(self, parent, controleur: ControleurBibliotheque, sur_statut):
        super().__init__(parent, fg_color="transparent")
        self.controleur = controleur
        self.sur_statut = sur_statut

        self._version_affichee = -1
        self._lignes: list[dict] = []
        self.map_livres_dispo: dict[str, str] = {}
        self.map_utilisateurs: dict[str, str] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="Emprunts et retours",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        cadre_emprunt = ctk.CTkFrame(self, corner_radius=10)
        cadre_emprunt.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        cadre_emprunt.grid_columnconfigure(0, weight=1)
        cadre_emprunt.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cadre_emprunt,
            text="Emprunter un livre",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=(12, 6), sticky="w")

        self.menu_livre = ctk.CTkOptionMenu(cadre_emprunt, values=["Aucun livre disponible"])
        self.menu_livre.grid(row=1, column=0, padx=(12, 6), pady=(0, 12), sticky="ew")

        self.menu_utilisateur = ctk.CTkOptionMenu(
            cadre_emprunt,
            values=["Aucun utilisateur"],
        )
        self.menu_utilisateur.grid(row=1, column=1, padx=6, pady=(0, 12), sticky="ew")

        self.bouton_emprunter = ctk.CTkButton(
            cadre_emprunt,
            text="Emprunter",
            width=120,
            command=self._emprunter,
        )
        self.bouton_emprunter.grid(row=1, column=2, padx=(6, 12), pady=(0, 12))

        entete_retours = ctk.CTkFrame(self, fg_color="transparent")
        entete_retours.grid(row=2, column=0, padx=16, pady=(12, 4), sticky="ew")
        entete_retours.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            entete_retours,
            text="Livres actuellement empruntés",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.label_nb_emprunts = ctk.CTkLabel(entete_retours, text="", text_color="gray")
        self.label_nb_emprunts.grid(row=0, column=1, sticky="e")

        self.liste_emprunts = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.liste_emprunts.grid(row=3, column=0, padx=16, pady=(4, 12), sticky="nsew")
        self.liste_emprunts.grid_columnconfigure(0, weight=1)

        self._label_vide = ctk.CTkLabel(
            self.liste_emprunts,
            text="Aucun livre n'est actuellement emprunté.",
            text_color="gray",
        )
        self._font_titre = ctk.CTkFont(size=14, weight="bold")
        self._font_detail = ctk.CTkFont(size=12)

    def _emprunter(self):
        isbn = self.map_livres_dispo.get(self.menu_livre.get(), "")
        id_utilisateur = self.map_utilisateurs.get(self.menu_utilisateur.get(), "")
        ok, message = self.controleur.emprunter_livre(isbn, id_utilisateur)
        self.sur_statut(message, ok)
        if ok:
            self.rafraichir()

    def _retourner(self, isbn: str):
        ok, message = self.controleur.retourner_livre(isbn)
        self.sur_statut(message, ok)
        if ok:
            self.rafraichir()

    def _creer_ligne(self, index: int) -> dict:
        cadre = ctk.CTkFrame(self.liste_emprunts, corner_radius=8)
        cadre.grid_columnconfigure(0, weight=1)

        label_titre = ctk.CTkLabel(cadre, text="", font=self._font_titre, anchor="w")
        label_titre.grid(row=0, column=0, padx=(12, 8), pady=(8, 0), sticky="w")

        label_detail = ctk.CTkLabel(
            cadre,
            text="",
            font=self._font_detail,
            text_color="gray",
            anchor="w",
        )
        label_detail.grid(row=1, column=0, padx=(12, 8), pady=(0, 8), sticky="w")

        bouton = ctk.CTkButton(cadre, text="Retourner", width=100, height=30)
        bouton.grid(row=0, column=1, rowspan=2, padx=12, pady=8)

        cadre.grid(row=index, column=0, padx=6, pady=4, sticky="ew")
        return {
            "cadre": cadre,
            "titre": label_titre,
            "detail": label_detail,
            "bouton": bouton,
        }

    def rafraichir(self):
        if self._version_affichee == self.controleur.version_donnees:
            return
        self._version_affichee = self.controleur.version_donnees

        livres_dispo = self.controleur.obtenir_livres_disponibles()
        utilisateurs = self.controleur.obtenir_tous_les_utilisateurs()

        self.map_livres_dispo = {
            f"{livre.get_title()} ({livre.get_isbn()})": livre.get_isbn()
            for livre in livres_dispo
        }
        self.map_utilisateurs = {
            f"{u.get_name()} ({u.get_user_id()})": u.get_user_id()
            for u in utilisateurs
        }

        if self.map_livres_dispo:
            options_livres = list(self.map_livres_dispo.keys())
            selection_courante = self.menu_livre.get()
            self.menu_livre.configure(values=options_livres, state="normal")
            self.menu_livre.set(
                selection_courante if selection_courante in self.map_livres_dispo else options_livres[0]
            )
        else:
            self.menu_livre.configure(values=["Aucun livre disponible"], state="disabled")
            self.menu_livre.set("Aucun livre disponible")

        if self.map_utilisateurs:
            options_utilisateurs = list(self.map_utilisateurs.keys())
            selection_user = self.menu_utilisateur.get()
            self.menu_utilisateur.configure(values=options_utilisateurs, state="normal")
            self.menu_utilisateur.set(
                selection_user if selection_user in self.map_utilisateurs else options_utilisateurs[0]
            )
        else:
            self.menu_utilisateur.configure(values=["Aucun utilisateur"], state="disabled")
            self.menu_utilisateur.set("Aucun utilisateur")

        peut_emprunter = bool(self.map_livres_dispo and self.map_utilisateurs)
        self.bouton_emprunter.configure(state="normal" if peut_emprunter else "disabled")

        empruntes = self.controleur.obtenir_livres_empruntes()
        self.label_nb_emprunts.configure(text=f"{len(empruntes)} livre(s) emprunté(s)")

        if not empruntes:
            for ligne in self._lignes:
                ligne["cadre"].grid_remove()
            self._label_vide.grid(row=0, column=0, pady=24)
            return

        self._label_vide.grid_remove()

        for index, livre in enumerate(empruntes):
            if index >= len(self._lignes):
                self._lignes.append(self._creer_ligne(index))
            else:
                self._lignes[index]["cadre"].grid(
                    row=index, column=0, padx=6, pady=4, sticky="ew"
                )

            id_emprunteur = livre.get_borrower_id()
            emprunteur = self.controleur.bibliotheque.find_user_by_id(id_emprunteur)
            nom_emprunteur = (
                f"{emprunteur.get_name()} ({id_emprunteur})"
                if emprunteur
                else id_emprunteur
            )
            isbn = livre.get_isbn()

            ligne = self._lignes[index]
            ligne["titre"].configure(text=livre.get_title())
            ligne["detail"].configure(
                text=f"{livre.get_author()}  •  ISBN : {isbn}  •  Emprunté par : {nom_emprunteur}"
            )
            ligne["bouton"].configure(
                command=lambda code=isbn: self._retourner(code)
            )

        for index in range(len(empruntes), len(self._lignes)):
            self._lignes[index]["cadre"].grid_remove()
