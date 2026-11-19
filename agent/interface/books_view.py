import unicodedata

import customtkinter as ctk
from tkinter import messagebox

from . import theme
from .widgets import BookCard, DialogueBase


def normaliser(texte):
    decompose = unicodedata.normalize("NFKD", texte.casefold())
    return "".join(
        caractere
        for caractere in decompose
        if not unicodedata.combining(caractere)
    )


class BooksView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        library,
        book_class,
        sur_modification_utilisateurs=None,
    ):
        super().__init__(master, fg_color="transparent")
        self.library = library
        self.book_class = book_class
        self.sur_modification_utilisateurs = sur_modification_utilisateurs
        self.filtre_etat = "tous"
        self.recherche_var = ctk.StringVar()
        self.filtre_mode = ctk.StringVar(value="Filtré par")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construire_entete()
        self._construire_corps()
        self.recherche_var.trace_add("write", lambda *_: self.rafraichir())
        self.rafraichir()

    def _construire_entete(self):
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 10))
        entete.grid_columnconfigure(0, weight=1)

        titres = ctk.CTkFrame(entete, fg_color="transparent")
        titres.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            titres,
            text="Bibliothèque",
            font=theme.police(30),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            titres,
            text="Livres",
            font=theme.police(13),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(anchor="w")

        outils = ctk.CTkFrame(entete, fg_color="transparent")
        outils.grid(row=0, column=1, sticky="e")

        cadre_recherche = ctk.CTkFrame(
            outils,
            fg_color=theme.CARTE,
            border_width=1,
            border_color=theme.BORDURE,
            corner_radius=16,
            width=280,
            height=34,
        )
        cadre_recherche.pack(side="left", padx=(0, 8))
        cadre_recherche.pack_propagate(False)

        ctk.CTkLabel(
            cadre_recherche,
            text="⌕",
            width=28,
            font=theme.police(20),
            text_color=theme.TEXTE_SECONDAIRE,
        ).pack(side="left", padx=(8, 0))
        self.entree_recherche = ctk.CTkEntry(
            cadre_recherche,
            textvariable=self.recherche_var,
            placeholder_text="Rechercher un livre",
            border_width=0,
            fg_color="transparent",
            text_color=theme.TEXTE,
            placeholder_text_color=theme.TEXTE_SECONDAIRE,
            font=theme.police(13),
            height=28,
        )
        self.entree_recherche.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.menu_filtre = ctk.CTkOptionMenu(
            outils,
            values=["Filtré par", "Titre", "Auteur"],
            variable=self.filtre_mode,
            command=lambda _: self.rafraichir(),
            width=150,
            height=34,
            corner_radius=4,
            fg_color=theme.CARTE,
            button_color=theme.BOUTON,
            button_hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            dropdown_fg_color=theme.CARTE,
            dropdown_hover_color=theme.BOUTON,
            dropdown_text_color=theme.TEXTE,
            font=theme.police(13),
            dropdown_font=theme.police(13),
        )
        self.menu_filtre.pack(side="left")

    def _construire_corps(self):
        corps = ctk.CTkFrame(self, fg_color="transparent")
        corps.grid(row=1, column=0, sticky="nsew", padx=24, pady=(4, 16))
        corps.grid_columnconfigure(0, weight=1)
        corps.grid_rowconfigure(0, weight=1)

        self.liste = ctk.CTkScrollableFrame(
            corps,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_fg_color=theme.FOND,
            scrollbar_button_color=theme.BOUTON,
            scrollbar_button_hover_color=theme.BOUTON_SURVOL,
        )
        self.liste.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        actions = ctk.CTkFrame(corps, fg_color="transparent", width=160)
        actions.grid(row=0, column=1, sticky="ne")

        self.boutons_etat = {
            "tous": self._bouton_action(
                actions,
                "Tous les livres",
                lambda: self._changer_etat("tous"),
            ),
            "disponible": self._bouton_action(
                actions,
                "Livre disponible",
                lambda: self._changer_etat("disponible"),
            ),
        }
        self.boutons_etat["tous"].pack(pady=(0, 8))
        self.boutons_etat["disponible"].pack(pady=(0, 8))
        self._bouton_action(actions, "Ajouter un livre", self.ajouter_livre).pack()

    def _bouton_action(self, parent, texte, commande):
        return ctk.CTkButton(
            parent,
            text=texte,
            width=150,
            height=32,
            corner_radius=4,
            fg_color=theme.BOUTON,
            hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            border_width=1,
            border_color=theme.BORDURE,
            font=theme.police(12),
            command=commande,
        )

    def _changer_etat(self, etat):
        self.filtre_etat = etat
        self.rafraichir()

    def _maj_boutons_etat(self):
        for etat, bouton in self.boutons_etat.items():
            bouton.configure(
                fg_color=theme.ACTIF if etat == self.filtre_etat else theme.BOUTON
            )

    def _livres_filtres(self):
        terme = normaliser(self.recherche_var.get().strip())
        mode = self.filtre_mode.get()
        resultat = []

        for livre in self.library.getAllBooks():
            if self.filtre_etat == "disponible" and not livre.getAvailability():
                continue

            if terme:
                titre = normaliser(livre.getTitle())
                auteur = normaliser(livre.getAuthor())
                isbn = normaliser(livre.getISBN())

                if mode == "Titre" and terme not in titre:
                    continue
                if mode == "Auteur" and terme not in auteur:
                    continue
                if mode not in ("Titre", "Auteur"):
                    if terme not in titre and terme not in auteur and terme not in isbn:
                        continue

            resultat.append(livre)

        return resultat

    def rafraichir(self):
        livres = self._livres_filtres()

        for enfant in self.liste.winfo_children():
            enfant.destroy()

        if not livres:
            ctk.CTkLabel(
                self.liste,
                text="Aucun livre ne correspond à votre recherche.",
                font=theme.police(14),
                text_color=theme.TEXTE_SECONDAIRE,
            ).pack(pady=48)
        else:
            for livre in livres:
                BookCard(
                    self.liste,
                    livre,
                    self.emprunter,
                    self.retourner,
                    self.supprimer,
                ).pack(fill="x", padx=2, pady=6)

        self._maj_boutons_etat()

    def ajouter_livre(self):
        dialogue = DialogueAjoutLivre(self, self.library)
        self.wait_window(dialogue)
        if dialogue.resultat:
            titre, auteur, isbn = dialogue.resultat
            self.library.addBook(self.book_class(titre, auteur, isbn))
            self.rafraichir()

    def emprunter(self, livre):
        utilisateurs = list(self.library.getAllUsers())
        if not utilisateurs:
            messagebox.showwarning(
                "Emprunter un livre",
                "Aucun utilisateur enregistré. Ajoutez d'abord un utilisateur.",
                parent=self,
            )
            return

        dialogue = DialogueEmprunt(self, livre, utilisateurs)
        self.wait_window(dialogue)
        if not dialogue.resultat:
            return

        if self.library.checkOutBook(livre.getISBN(), dialogue.resultat):
            self.rafraichir()
            if self.sur_modification_utilisateurs:
                self.sur_modification_utilisateurs()
        else:
            messagebox.showerror(
                "Emprunter un livre",
                "Impossible d'emprunter ce livre. Vérifiez sa disponibilité.",
                parent=self,
            )

    def retourner(self, livre):
        if self.library.returnBook(livre.getISBN()):
            self.rafraichir()
            if self.sur_modification_utilisateurs:
                self.sur_modification_utilisateurs()
        else:
            messagebox.showerror(
                "Retourner un livre",
                "Impossible de retourner ce livre.",
                parent=self,
            )

    def supprimer(self, livre):
        if not livre.getAvailability():
            messagebox.showerror(
                "Suppression impossible",
                f"« {livre.getTitle()} » est emprunté par "
                f"{livre.getBorrowerId()}.\nRetournez-le avant de le supprimer.",
                parent=self,
            )
            return

        if not messagebox.askyesno(
            "Supprimer un livre",
            f"Supprimer « {livre.getTitle()} » ?",
            parent=self,
        ):
            return

        if self.library.removeBook(livre.getISBN()):
            self.rafraichir()
        else:
            messagebox.showerror(
                "Supprimer un livre",
                "Impossible de supprimer ce livre.",
                parent=self,
            )


class DialogueAjoutLivre(DialogueBase):
    def __init__(self, master, library):
        super().__init__(master, "Ajouter un livre", 380, 300)
        self.library = library

        self.entree_titre = self._champ(self, "Titre")
        self.entree_auteur = self._champ(self, "Auteur")
        self.entree_isbn = self._champ(self, "ISBN")
        self._boutons(self, "Ajouter", self.valider)

        self.entree_titre.focus_set()
        self.bind("<Return>", lambda _: self.valider())

    def valider(self):
        titre = self.entree_titre.get().strip()
        auteur = self.entree_auteur.get().strip()
        isbn = self.entree_isbn.get().strip()

        if not titre or not auteur or not isbn:
            messagebox.showwarning(
                "Champs requis",
                "Le titre, l'auteur et l'ISBN sont obligatoires.",
                parent=self,
            )
            return

        if any("|" in valeur for valeur in (titre, auteur, isbn)):
            messagebox.showerror(
                "Caractère interdit",
                "Le caractère « | » ne peut pas être utilisé dans les champs.",
                parent=self,
            )
            return

        if self.library.findBookByISBN(isbn):
            messagebox.showerror(
                "ISBN existant",
                f"Un livre avec l'ISBN {isbn} existe déjà.",
                parent=self,
            )
            return

        self.resultat = (titre, auteur, isbn)
        self.destroy()


class DialogueEmprunt(DialogueBase):
    def __init__(self, master, livre, utilisateurs):
        super().__init__(master, "Emprunter un livre", 420, 250)
        self.utilisateurs = {
            f"{utilisateur.getName()} ({utilisateur.getUserId()})": utilisateur.getUserId()
            for utilisateur in utilisateurs
        }

        ctk.CTkLabel(
            self,
            text=livre.getTitle(),
            font=theme.police(15, "bold"),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(18, 2))
        ctk.CTkLabel(
            self,
            text="Choisissez l'utilisateur qui emprunte ce livre.",
            font=theme.police(12),
            text_color=theme.TEXTE_SECONDAIRE,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 8))

        valeurs = list(self.utilisateurs)
        self.combo_utilisateur = ctk.CTkComboBox(
            self,
            values=valeurs,
            state="readonly",
            height=32,
            corner_radius=4,
            border_width=1,
            border_color=theme.BORDURE,
            fg_color=theme.CARTE,
            button_color=theme.BOUTON,
            button_hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            dropdown_fg_color=theme.CARTE,
            dropdown_hover_color=theme.BOUTON,
            dropdown_text_color=theme.TEXTE,
            font=theme.police(13),
            dropdown_font=theme.police(13),
        )
        self.combo_utilisateur.set(valeurs[0])
        self.combo_utilisateur.pack(fill="x", padx=20)

        self._boutons(self, "Emprunter", self.valider)

    def valider(self):
        choix = self.combo_utilisateur.get()
        if choix not in self.utilisateurs:
            messagebox.showwarning(
                "Utilisateur requis",
                "Choisissez un utilisateur.",
                parent=self,
            )
            return

        self.resultat = self.utilisateurs[choix]
        self.destroy()
