from tkinter import StringVar, messagebox, ttk

import customtkinter as ctk

from dialogue_ajout_livre import DialogueAjoutLivre
from dialogue_emprunt_livre import DialogueEmpruntLivre
from donnees import COMMANDE_COMPILATION
from theme import (
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
    POLICE_BOUTON,
    POLICE_BOUTON_SECONDAIRE,
    POLICE_NORMALE,
    POLICE_PETITE,
    RAYON,
    STYLE_TABLEAU,
)

COLONNES = (
    ("titre", "Titre", 210, 120),
    ("auteur", "Auteur", 210, 120),
    ("isbn", "ISBN", 150, 110),
    ("statut", "Statut", 100, 90),
    ("emprunteur", "Emprunteur", 100, 90),
)


class EcranPrincipal(ctk.CTkFrame):
    def __init__(
        self,
        parent: ctk.CTkFrame,
        bibliotheque=None,
        erreur: str | None = None,
        on_mutation=None,
        on_sauvegarder=None,
        on_backup=None,
    ) -> None:
        super().__init__(parent, fg_color=COULEUR_FOND, corner_radius=0)
        self.bibliotheque = bibliotheque
        self.erreur = erreur
        self.on_mutation = on_mutation
        self.on_sauvegarder = on_sauvegarder
        self.on_backup = on_backup
        self._construire_filtres()
        self._construire_erreur()
        self._construire_tableau()
        self._construire_actions()
        self.recherche_var.trace_add("write", self._on_recherche_change)
        self._rafraichir_tableau()

    def _construire_filtres(self) -> None:
        filtres = ctk.CTkFrame(self, fg_color="transparent")
        filtres.pack(fill="x", padx=24, pady=(20, 12))
        filtres.grid_columnconfigure(0, weight=1)
        filtres.grid_columnconfigure(1, weight=0)
        filtres.grid_columnconfigure(2, weight=0)

        label_rechercher = ctk.CTkLabel(
            filtres,
            text="Rechercher",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        label_rechercher.grid(row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 4))

        self.recherche_var = StringVar()
        self.champ_recherche = ctk.CTkEntry(
            filtres,
            height=HAUTEUR_CHAMP,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
            fg_color=COULEUR_FOND,
            text_color=COULEUR_TEXTE,
            textvariable=self.recherche_var,
            placeholder_text="Titre ou auteur…",
            placeholder_text_color=COULEUR_TEXTE_PLACEHOLDER,
            font=POLICE_NORMALE,
        )
        self.champ_recherche.grid(row=1, column=0, sticky="ew", padx=(0, 12))

        label_par = ctk.CTkLabel(
            filtres,
            text="Par",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        label_par.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=(0, 4))

        self.choix_par = ctk.CTkComboBox(
            filtres,
            values=["Titre", "Auteur", "ISBN"],
            width=140,
            height=HAUTEUR_CHAMP,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
            fg_color=COULEUR_FOND,
            button_color=COULEUR_FOND,
            button_hover_color=COULEUR_SURVOL,
            text_color=COULEUR_TEXTE,
            dropdown_fg_color=COULEUR_FOND,
            dropdown_hover_color=COULEUR_SURVOL,
            dropdown_text_color=COULEUR_TEXTE,
            font=POLICE_NORMALE,
            dropdown_font=POLICE_NORMALE,
            state="readonly",
            command=lambda valeur: self._rafraichir_tableau(),
        )
        self.choix_par.set("Titre")
        self.choix_par.grid(row=1, column=1, sticky="w", padx=(0, 12))

        self.filtre_disponibles = ctk.CTkCheckBox(
            filtres,
            text="Disponibles seulement",
            font=POLICE_NORMALE,
            text_color=COULEUR_TEXTE_MENU,
            fg_color=COULEUR_PRIMAIRE,
            hover_color=COULEUR_PRIMAIRE_SURVOL,
            border_color=COULEUR_BORDURE,
            checkbox_width=14,
            checkbox_height=14,
            corner_radius=3,
            command=self._rafraichir_tableau,
        )
        self.filtre_disponibles.grid(row=1, column=2, sticky="w")

    def _construire_erreur(self) -> None:
        if not self.erreur:
            return

        cadre = ctk.CTkFrame(
            self,
            fg_color=COULEUR_FOND,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_ERREUR,
        )
        cadre.pack(fill="x", padx=24, pady=(0, 12))

        message = ctk.CTkLabel(
            cadre,
            text=(
                f"Impossible de charger les données : {self.erreur}\n"
                f"Compilez le module avec :\n{COMMANDE_COMPILATION}"
            ),
            font=POLICE_PETITE,
            text_color=COULEUR_ERREUR,
            anchor="w",
            justify="left",
            wraplength=760,
        )
        message.pack(fill="x", padx=12, pady=10)

    def _on_recherche_change(self, *args) -> None:
        self._rafraichir_tableau()

    def _rafraichir_tableau(self) -> None:
        if self.bibliotheque is None:
            self._afficher_livres([])
            return

        texte = self.recherche_var.get().strip()
        mode = self.choix_par.get()
        disponibles_seulement = bool(self.filtre_disponibles.get())

        if not texte:
            livres = (
                self.bibliotheque.available_books()
                if disponibles_seulement
                else self.bibliotheque.all_books()
            )
        elif mode == "Titre":
            livres = self.bibliotheque.search_books_by_title(texte)
        elif mode == "Auteur":
            livres = self.bibliotheque.search_books_by_author(texte)
        else:
            livre = self.bibliotheque.find_book_by_isbn(texte)
            livres = [livre] if livre is not None else []

        if disponibles_seulement and texte:
            livres = [livre for livre in livres if livre.available]

        self._afficher_livres(livres)

    def _afficher_livres(self, livres) -> None:
        for element in self.tableau.get_children():
            self.tableau.delete(element)

        for livre in livres:
            statut = "Disponible" if livre.available else "Emprunté"
            emprunteur = livre.borrower_id or "—"
            self.tableau.insert(
                "",
                "end",
                values=(
                    livre.title,
                    livre.author,
                    livre.isbn,
                    statut,
                    emprunteur,
                ),
            )

    def _construire_tableau(self) -> None:
        cadre_tableau = ctk.CTkFrame(
            self,
            fg_color=COULEUR_FOND,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE,
        )
        cadre_tableau.pack(fill="both", expand=True, padx=24)

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

    def _construire_actions(self) -> None:
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(16, 20))

        bouton_ajouter = self._bouton_primaire(
            actions,
            "Ajouter un livre",
            150,
            commande=self._ouvrir_dialogue_ajout,
        )
        bouton_ajouter.pack(side="left")

        for texte, largeur, commande in (
            ("Supprimer", 100, self._supprimer_livre),
            ("Emprunter", 100, self._ouvrir_dialogue_emprunt),
            ("Retourner", 100, self._retourner_livre),
        ):
            bouton = self._bouton_secondaire(
                actions,
                texte,
                largeur,
                commande,
            )
            bouton.pack(side="left", padx=(10, 0))

        bouton_copie = self._bouton_secondaire(
            actions,
            "Créer une copie",
            140,
            commande=self._creer_backup,
        )
        bouton_copie.pack(side="right")

        bouton_sauvegarder = self._bouton_secondaire(
            actions,
            "Sauvegarder",
            130,
            commande=self._sauvegarder,
        )
        bouton_sauvegarder.pack(side="right", padx=(0, 10))

        self.label_action = ctk.CTkLabel(
            self,
            text="",
            height=18,
            font=POLICE_PETITE,
            text_color=COULEUR_TEXTE_SECONDAIRE,
            anchor="w",
        )
        self.label_action.pack(fill="x", padx=24, pady=(0, 12))

    def _afficher_message(self, message: str, erreur: bool = False) -> None:
        self.label_action.configure(
            text=message,
            text_color=COULEUR_ERREUR if erreur else COULEUR_TEXTE_SECONDAIRE,
        )

    def _effacer_message(self) -> None:
        self.label_action.configure(text="")

    def _sauvegarder(self) -> None:
        self._effacer_message()
        if self.on_sauvegarder is None or not self.on_sauvegarder():
            self._afficher_message("Erreur lors de la sauvegarde.", erreur=True)
            return
        self._afficher_message("Données sauvegardées.")

    def _creer_backup(self) -> None:
        self._effacer_message()
        if self.on_backup is None or not self.on_backup():
            self._afficher_message(
                "Impossible de créer la copie : un fichier .backup existe déjà. "
                "Supprimez-le pour en créer un nouveau.",
                erreur=True,
            )
            return
        self._afficher_message("Copie créée.")

    def _livre_selectionne(self):
        if self.bibliotheque is None:
            self._afficher_message("La bibliothèque n'est pas chargée.", erreur=True)
            return None

        selection = self.tableau.selection()
        if not selection:
            self._afficher_message("Sélectionnez un livre.", erreur=True)
            return None

        isbn = self.tableau.item(selection[0], "values")[2]
        livre = self.bibliotheque.find_book_by_isbn(isbn)
        if livre is None:
            self._afficher_message("Livre introuvable.", erreur=True)
            return None
        return livre

    def _apres_mutation(self) -> None:
        self._rafraichir_tableau()
        if self.on_mutation is not None:
            self.on_mutation()

    def _ouvrir_dialogue_ajout(self) -> None:
        self._effacer_message()
        dialogue = DialogueAjoutLivre(
            self.winfo_toplevel(),
            self.bibliotheque,
        )
        self.wait_window(dialogue)
        if dialogue.ajout_reussi:
            self._apres_mutation()
            self._afficher_message("Livre ajouté.")

    def _ouvrir_dialogue_emprunt(self) -> None:
        self._effacer_message()
        livre = self._livre_selectionne()
        if livre is None:
            return

        dialogue = DialogueEmpruntLivre(
            self.winfo_toplevel(),
            self.bibliotheque,
            livre,
        )
        self.wait_window(dialogue)
        if dialogue.emprunt_reussi:
            self._apres_mutation()
            self._afficher_message("Livre emprunté.")

    def _retourner_livre(self) -> None:
        self._effacer_message()
        livre = self._livre_selectionne()
        if livre is None:
            return

        if self.bibliotheque.return_book(livre.isbn):
            self._apres_mutation()
            self._afficher_message("Livre retourné.")
        else:
            self._afficher_message(
                "Impossible de retourner ce livre : il n'est pas emprunté.",
                erreur=True,
            )

    def _supprimer_livre(self) -> None:
        self._effacer_message()
        livre = self._livre_selectionne()
        if livre is None:
            return

        if not livre.available:
            self._afficher_message(
                "Impossible de supprimer un livre emprunté. Retournez-le d'abord.",
                erreur=True,
            )
            return

        confirmation = messagebox.askyesno(
            "Supprimer un livre",
            f"Supprimer « {livre.title} » ?",
            parent=self.winfo_toplevel(),
        )
        if not confirmation:
            return

        if self.bibliotheque.remove_book(livre.isbn):
            self._apres_mutation()
            self._afficher_message("Livre supprimé.")
        else:
            self._afficher_message("Livre introuvable.", erreur=True)

    def _bouton_primaire(
        self,
        parent: ctk.CTkFrame,
        texte: str,
        largeur: int,
        commande=None,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=texte,
            command=commande,
            width=largeur,
            height=HAUTEUR_BOUTON,
            corner_radius=RAYON,
            fg_color=COULEUR_PRIMAIRE,
            hover_color=COULEUR_PRIMAIRE_SURVOL,
            text_color="#ffffff",
            font=POLICE_BOUTON,
        )

    def _bouton_secondaire(
        self,
        parent: ctk.CTkFrame,
        texte: str,
        largeur: int,
        commande=None,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=texte,
            command=commande,
            width=largeur,
            height=HAUTEUR_BOUTON,
            corner_radius=RAYON,
            fg_color=COULEUR_FOND,
            hover_color=COULEUR_SURVOL,
            border_width=1,
            border_color=COULEUR_BORDURE,
            text_color=COULEUR_TEXTE,
            font=POLICE_BOUTON_SECONDAIRE,
        )
