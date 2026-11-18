import customtkinter as ctk

from theme import (
    COULEUR_BANDEAU,
    COULEUR_BORDURE,
    COULEUR_ERREUR,
    COULEUR_FOND,
    COULEUR_PRIMAIRE,
    COULEUR_PRIMAIRE_SURVOL,
    COULEUR_SURVOL,
    COULEUR_TEXTE,
    COULEUR_TEXTE_MENU,
    COULEUR_TEXTE_PLACEHOLDER,
    COULEUR_TEXTE_SECONDAIRE,
    HAUTEUR_BOUTON,
    HAUTEUR_CHAMP,
    HAUTEUR_DIALOGUE,
    HAUTEUR_ENTETE,
    LARGEUR_DIALOGUE,
    MARGE_DIALOGUE,
    POLICE_BOUTON,
    POLICE_BOUTON_SECONDAIRE,
    POLICE_GRASSE,
    POLICE_NORMALE,
    POLICE_PETITE,
    RAYON,
)

HAUTEUR_APERCU = 86


class DialogueEmpruntLivre(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk, bibliotheque, livre) -> None:
        super().__init__(parent, fg_color=COULEUR_FOND)
        self.bibliotheque = bibliotheque
        self.livre = livre
        self.emprunt_reussi = False
        self.utilisateurs_par_libelle: dict[str, str] = {}
        self.title("Emprunter un livre")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._fermer)

        self._construire_entete()
        self._construire_actions()
        self._construire_contenu()

        self._centrer(parent)
        self.wait_visibility()
        self.grab_set()
        self.focus_force()

    def _construire_entete(self) -> None:
        entete = ctk.CTkFrame(
            self,
            height=HAUTEUR_ENTETE,
            fg_color=COULEUR_BANDEAU,
            corner_radius=0,
            border_width=1,
            border_color=COULEUR_BORDURE,
        )
        entete.pack(fill="x")
        entete.pack_propagate(False)

        titre = ctk.CTkLabel(
            entete,
            text="Emprunter un livre",
            font=POLICE_GRASSE,
            text_color=COULEUR_TEXTE,
            anchor="w",
        )
        titre.pack(fill="both", expand=True, padx=14)

    def _construire_actions(self) -> None:
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(
            side="bottom",
            fill="x",
            padx=MARGE_DIALOGUE,
            pady=MARGE_DIALOGUE,
        )

        bouton_confirmer = ctk.CTkButton(
            actions,
            text="Confirmer",
            command=self._confirmer,
            width=100,
            height=HAUTEUR_BOUTON,
            corner_radius=RAYON,
            fg_color=COULEUR_PRIMAIRE,
            hover_color=COULEUR_PRIMAIRE_SURVOL,
            text_color="#ffffff",
            font=POLICE_BOUTON,
        )
        bouton_confirmer.pack(side="right")

        bouton_annuler = ctk.CTkButton(
            actions,
            text="Annuler",
            command=self._fermer,
            width=100,
            height=HAUTEUR_BOUTON,
            corner_radius=RAYON,
            fg_color=COULEUR_FOND,
            hover_color=COULEUR_SURVOL,
            border_width=1,
            border_color=COULEUR_BORDURE,
            text_color=COULEUR_TEXTE,
            font=POLICE_BOUTON_SECONDAIRE,
        )
        bouton_annuler.pack(side="right", padx=(0, 10))

    def _construire_contenu(self) -> None:
        contenu = ctk.CTkFrame(self, fg_color=COULEUR_FOND, corner_radius=0)
        contenu.pack(
            fill="both",
            expand=True,
            padx=MARGE_DIALOGUE,
            pady=(MARGE_DIALOGUE, 0),
        )

        self.champ_isbn = self._ajouter_champ(
            contenu,
            "ISBN du livre",
            "Saisir l'ISBN",
        )
        self.champ_isbn.insert(0, self.livre.isbn)
        self.champ_isbn.configure(state="disabled")

        label_utilisateur = ctk.CTkLabel(
            contenu,
            text="Utilisateur",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        label_utilisateur.pack(fill="x", pady=(0, 4))

        if self.bibliotheque is not None:
            for utilisateur in self.bibliotheque.all_users():
                libelle = f"{utilisateur.name} ({utilisateur.user_id})"
                self.utilisateurs_par_libelle[libelle] = utilisateur.user_id

        valeurs = ["Sélectionner un utilisateur", *self.utilisateurs_par_libelle]

        self.combo_utilisateur = ctk.CTkComboBox(
            contenu,
            values=valeurs,
            height=HAUTEUR_CHAMP,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
            fg_color=COULEUR_FOND,
            button_color=COULEUR_FOND,
            button_hover_color=COULEUR_SURVOL,
            text_color=COULEUR_TEXTE_PLACEHOLDER,
            dropdown_fg_color=COULEUR_FOND,
            dropdown_hover_color=COULEUR_SURVOL,
            dropdown_text_color=COULEUR_TEXTE,
            font=POLICE_NORMALE,
            dropdown_font=POLICE_NORMALE,
            state="readonly",
        )
        self.combo_utilisateur.set("Sélectionner un utilisateur")
        self.combo_utilisateur.pack(fill="x", pady=(0, 14))

        self._construire_apercu(contenu)
        self.apercu_titre.configure(text=self.livre.title)
        self.apercu_auteur.configure(text=self.livre.author)
        self.apercu_statut.configure(
            text=f"Statut : {'Disponible' if self.livre.available else 'Emprunté'}"
        )

        self.label_erreur = ctk.CTkLabel(
            contenu,
            text="",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_ERREUR,
            anchor="w",
        )
        self.label_erreur.pack(fill="x", pady=(8, 0))

    def _construire_apercu(self, parent: ctk.CTkFrame) -> None:
        apercu = ctk.CTkFrame(
            parent,
            height=HAUTEUR_APERCU,
            fg_color=COULEUR_FOND,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
        )
        apercu.pack(fill="x")
        apercu.pack_propagate(False)

        self.apercu_titre = ctk.CTkLabel(
            apercu,
            text="—",
            height=20,
            font=POLICE_GRASSE,
            text_color=COULEUR_TEXTE_MENU,
            anchor="w",
        )
        self.apercu_titre.pack(fill="x", padx=12, pady=(10, 0))

        self.apercu_auteur = ctk.CTkLabel(
            apercu,
            text="—",
            height=20,
            font=POLICE_NORMALE,
            text_color=COULEUR_TEXTE_MENU,
            anchor="w",
        )
        self.apercu_auteur.pack(fill="x", padx=12, pady=(2, 0))

        self.apercu_statut = ctk.CTkLabel(
            apercu,
            text="Statut : —",
            height=20,
            font=POLICE_NORMALE,
            text_color=COULEUR_TEXTE_MENU,
            anchor="w",
        )
        self.apercu_statut.pack(fill="x", padx=12, pady=(2, 0))

    def _ajouter_champ(
        self,
        parent: ctk.CTkFrame,
        texte: str,
        placeholder: str,
    ) -> ctk.CTkEntry:
        etiquette = ctk.CTkLabel(
            parent,
            text=texte,
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        etiquette.pack(fill="x", pady=(0, 4))

        champ = ctk.CTkEntry(
            parent,
            height=HAUTEUR_CHAMP,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
            fg_color=COULEUR_FOND,
            text_color=COULEUR_TEXTE,
            placeholder_text=placeholder,
            placeholder_text_color=COULEUR_TEXTE_PLACEHOLDER,
            font=POLICE_NORMALE,
        )
        champ.pack(fill="x", pady=(0, 14))
        return champ

    def _confirmer(self) -> None:
        if self.bibliotheque is None:
            self._afficher_erreur("La bibliothèque n'est pas chargée.")
            return

        libelle = self.combo_utilisateur.get()
        user_id = self.utilisateurs_par_libelle.get(libelle)
        if user_id is None:
            self._afficher_erreur("Sélectionnez un utilisateur.")
            return

        if not self.bibliotheque.check_out_book(self.livre.isbn, user_id):
            if not self.livre.available:
                self._afficher_erreur("Ce livre est déjà emprunté.")
            else:
                self._afficher_erreur("L'emprunt a échoué.")
            return

        self.emprunt_reussi = True
        self._fermer()

    def _afficher_erreur(self, message: str) -> None:
        self.label_erreur.configure(text=message)

    def _centrer(self, parent: ctk.CTk) -> None:
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - LARGEUR_DIALOGUE) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - HAUTEUR_DIALOGUE) // 2
        self.geometry(f"{LARGEUR_DIALOGUE}x{HAUTEUR_DIALOGUE}+{x}+{y}")

    def _fermer(self) -> None:
        self.grab_release()
        self.destroy()
