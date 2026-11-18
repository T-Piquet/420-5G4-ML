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


class DialogueAjoutLivre(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk, bibliotheque) -> None:
        super().__init__(parent, fg_color=COULEUR_FOND)
        self.bibliotheque = bibliotheque
        self.ajout_reussi = False
        self.title("Ajouter un livre")
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
            text="Ajouter un livre",
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

        bouton_ajouter = ctk.CTkButton(
            actions,
            text="Ajouter",
            command=self._ajouter,
            width=100,
            height=HAUTEUR_BOUTON,
            corner_radius=RAYON,
            fg_color=COULEUR_PRIMAIRE,
            hover_color=COULEUR_PRIMAIRE_SURVOL,
            text_color="#ffffff",
            font=POLICE_BOUTON,
        )
        bouton_ajouter.pack(side="right")

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

        self.champ_titre = self._ajouter_champ(contenu, "Titre", "Saisir le titre")
        self.champ_auteur = self._ajouter_champ(
            contenu,
            "Auteur",
            "Saisir l'auteur",
        )
        self.champ_isbn = self._ajouter_champ(contenu, "ISBN", "Saisir l'ISBN")

        self.label_erreur = ctk.CTkLabel(
            contenu,
            text="",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_ERREUR,
            anchor="w",
        )
        self.label_erreur.pack(fill="x")

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

    def _ajouter(self) -> None:
        self.label_erreur.configure(text="")

        if self.bibliotheque is None:
            self._afficher_erreur("La bibliothèque n'est pas chargée.")
            return

        titre = self.champ_titre.get().strip()
        auteur = self.champ_auteur.get().strip()
        isbn = self.champ_isbn.get().strip()
        if not titre or not auteur or not isbn:
            self._afficher_erreur("Tous les champs sont obligatoires.")
            return

        if not self.bibliotheque.add_book(titre, auteur, isbn):
            self._afficher_erreur("Un livre avec cet ISBN existe déjà.")
            return

        self.ajout_reussi = True
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
