import argparse
from pathlib import Path
from tkinter import messagebox, ttk

import customtkinter as ctk

from donnees import (
    REPERTOIRE_DONNEES,
    charger_bibliotheque,
    creer_backup,
    sauvegarder_bibliotheque,
)
from ecran_principal import EcranPrincipal
from ecran_utilisateurs import EcranUtilisateurs
from theme import (
    COULEUR_ACTIF,
    COULEUR_BANDEAU,
    COULEUR_BORDURE_LEGERE,
    COULEUR_ENTETE_TABLEAU,
    COULEUR_FOND,
    COULEUR_MENU,
    COULEUR_SIDEBAR,
    COULEUR_SURVOL,
    COULEUR_TEXTE,
    COULEUR_TEXTE_ACTIF,
    COULEUR_TEXTE_MENU,
    COULEUR_TEXTE_SECONDAIRE,
    HAUTEUR_ENTETE,
    HAUTEUR_FENETRE,
    HAUTEUR_LIGNE_TABLEAU,
    HAUTEUR_MENU,
    HAUTEUR_MIN,
    LARGEUR_FENETRE,
    LARGEUR_MIN,
    LARGEUR_SIDEBAR,
    POLICE_GRASSE,
    POLICE_NAV,
    POLICE_NAV_ACTIVE,
    POLICE_NORMALE,
    POLICE_PETITE,
    RAYON,
    STYLE_TABLEAU,
)

ECRANS = {
    "livres": EcranPrincipal,
    "utilisateurs": EcranUtilisateurs,
}


def configurer_style_tableau() -> None:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        STYLE_TABLEAU,
        background=COULEUR_FOND,
        fieldbackground=COULEUR_FOND,
        foreground=COULEUR_TEXTE,
        rowheight=HAUTEUR_LIGNE_TABLEAU,
        font=POLICE_NORMALE,
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        f"{STYLE_TABLEAU}.Heading",
        background=COULEUR_ENTETE_TABLEAU,
        foreground=COULEUR_TEXTE,
        font=POLICE_GRASSE,
        relief="flat",
        borderwidth=0,
        padding=(10, 8),
    )
    style.map(
        STYLE_TABLEAU,
        background=[("selected", COULEUR_ACTIF)],
        foreground=[("selected", COULEUR_TEXTE_ACTIF)],
    )
    style.map(
        f"{STYLE_TABLEAU}.Heading",
        background=[("active", COULEUR_ENTETE_TABLEAU)],
        foreground=[("active", COULEUR_TEXTE)],
    )


class Application(ctk.CTk):
    def __init__(self, repertoire_donnees=None) -> None:
        super().__init__(fg_color=COULEUR_FOND)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Système de gestion de bibliothèque")
        self.geometry(f"{LARGEUR_FENETRE}x{HAUTEUR_FENETRE}")
        self.minsize(LARGEUR_MIN, HAUTEUR_MIN)
        self.protocol("WM_DELETE_WINDOW", self._fermer)

        self.repertoire_donnees = (
            Path(repertoire_donnees)
            if repertoire_donnees is not None
            else REPERTOIRE_DONNEES
        )
        self.modifie = False
        self.ecran_actuel: ctk.CTkFrame | None = None
        self.boutons_navigation: dict[str, ctk.CTkButton] = {}
        self.labels_stats: dict[str, tuple[ctk.CTkLabel, str]] = {}
        self.erreur_chargement: str | None = None

        try:
            self.bibliotheque = charger_bibliotheque(self.repertoire_donnees)
        except Exception as erreur:
            self.bibliotheque = None
            self.erreur_chargement = str(erreur)

        configurer_style_tableau()
        self._construire_interface()
        self._mettre_a_jour_statistiques()
        self.afficher_ecran("livres")

    def _construire_interface(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._construire_entete()
        self._construire_menu()
        self._construire_corps()

    def _construire_entete(self) -> None:
        entete = ctk.CTkFrame(
            self,
            height=HAUTEUR_ENTETE,
            fg_color=COULEUR_BANDEAU,
            corner_radius=0,
        )
        entete.grid(row=0, column=0, sticky="ew")
        entete.grid_propagate(False)
        entete.grid_columnconfigure(0, weight=1)

        titre = ctk.CTkLabel(
            entete,
            text="Système de gestion de bibliothèque",
            font=POLICE_GRASSE,
            text_color=COULEUR_TEXTE,
            anchor="w",
        )
        titre.grid(row=0, column=0, sticky="w", padx=14)

    def _construire_menu(self) -> None:
        menu = ctk.CTkFrame(
            self,
            height=HAUTEUR_MENU,
            fg_color=COULEUR_MENU,
            corner_radius=0,
            border_width=1,
            border_color=COULEUR_BORDURE_LEGERE,
        )
        menu.grid(row=1, column=0, sticky="ew")
        menu.grid_propagate(False)

        bouton_fichier = self._bouton_menu(menu, "Fichier", None, 50)
        bouton_fichier.pack(side="left", padx=(14, 10), pady=2)

        bouton_livres = self._bouton_menu(
            menu,
            "Livres",
            lambda: self.afficher_ecran("livres"),
            46,
        )
        bouton_livres.pack(side="left", padx=(0, 10), pady=2)

        bouton_utilisateurs = self._bouton_menu(
            menu,
            "Utilisateurs",
            lambda: self.afficher_ecran("utilisateurs"),
            80,
        )
        bouton_utilisateurs.pack(side="left", pady=2)

    def _bouton_menu(
        self,
        parent: ctk.CTkFrame,
        texte: str,
        commande,
        largeur: int,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=texte,
            command=commande,
            width=largeur,
            height=28,
            corner_radius=RAYON,
            fg_color="transparent",
            hover_color=COULEUR_SURVOL,
            text_color=COULEUR_TEXTE_MENU,
            font=POLICE_NORMALE,
            anchor="w",
        )

    def _construire_corps(self) -> None:
        corps = ctk.CTkFrame(self, fg_color=COULEUR_FOND, corner_radius=0)
        corps.grid(row=2, column=0, sticky="nsew")
        corps.grid_columnconfigure(0, minsize=LARGEUR_SIDEBAR)
        corps.grid_columnconfigure(1, weight=1)
        corps.grid_rowconfigure(0, weight=1)

        self._construire_sidebar(corps)

        self.conteneur = ctk.CTkFrame(
            corps,
            fg_color=COULEUR_FOND,
            corner_radius=0,
        )
        self.conteneur.grid(row=0, column=1, sticky="nsew")

    def _construire_sidebar(self, parent: ctk.CTkFrame) -> None:
        sidebar = ctk.CTkFrame(
            parent,
            width=LARGEUR_SIDEBAR,
            fg_color=COULEUR_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=COULEUR_BORDURE_LEGERE,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")

        navigation = ctk.CTkFrame(sidebar, fg_color="transparent")
        navigation.pack(fill="x", padx=12, pady=(16, 0))

        for nom, texte in (("livres", "Livres"), ("utilisateurs", "Utilisateurs")):
            bouton = ctk.CTkButton(
                navigation,
                text=texte,
                height=38,
                corner_radius=RAYON,
                fg_color="transparent",
                hover_color=COULEUR_SURVOL,
                text_color=COULEUR_TEXTE_MENU,
                font=POLICE_NAV,
                anchor="w",
                command=lambda nom_ecran=nom: self.afficher_ecran(nom_ecran),
            )
            bouton.pack(fill="x", pady=2)
            self.boutons_navigation[nom] = bouton

        statistiques = ctk.CTkFrame(
            sidebar,
            fg_color=COULEUR_FOND,
            corner_radius=RAYON,
            border_width=1,
            border_color=COULEUR_BORDURE_LEGERE,
        )
        statistiques.pack(side="bottom", fill="x", padx=12, pady=12)

        titre_stats = ctk.CTkLabel(
            statistiques,
            text="Statistiques",
            height=20,
            font=POLICE_GRASSE,
            text_color=COULEUR_TEXTE,
            anchor="w",
        )
        titre_stats.pack(fill="x", padx=12, pady=(12, 4))

        for cle, libelle in (
            ("total", "Total des livres"),
            ("disponibles", "Disponibles"),
            ("empruntes", "Empruntés"),
            ("utilisateurs", "Utilisateurs"),
        ):
            valeur = ctk.CTkLabel(
                statistiques,
                text=f"{libelle} : —",
                height=18,
                font=POLICE_PETITE,
                text_color=COULEUR_TEXTE_SECONDAIRE,
                anchor="w",
            )
            valeur.pack(fill="x", padx=12, pady=2)
            self.labels_stats[cle] = (valeur, libelle)

    def _mettre_a_jour_statistiques(self) -> None:
        if self.bibliotheque is None:
            valeurs = {cle: "—" for cle in self.labels_stats}
        else:
            valeurs = {
                "total": self.bibliotheque.total_books,
                "disponibles": self.bibliotheque.available_count,
                "empruntes": self.bibliotheque.checked_out_count,
                "utilisateurs": self.bibliotheque.users_count,
            }

        for cle, (label, libelle) in self.labels_stats.items():
            label.configure(text=f"{libelle} : {valeurs[cle]}")

    def _apres_mutation(self) -> None:
        self.modifie = True
        self._mettre_a_jour_statistiques()

    def _sauvegarder(self) -> bool:
        if self.bibliotheque is None:
            return False

        succes = sauvegarder_bibliotheque(
            self.bibliotheque,
            self.repertoire_donnees,
        )
        if succes:
            self.modifie = False
        return succes

    def _creer_backup(self) -> bool:
        if self.bibliotheque is None:
            return False
        return creer_backup(self.repertoire_donnees)

    def _fermer(self) -> None:
        if not self.modifie:
            self.destroy()
            return

        reponse = messagebox.askyesnocancel(
            "Quitter",
            "Des modifications ne sont pas sauvegardées. "
            "Voulez-vous sauvegarder avant de quitter ?",
            parent=self,
        )
        if reponse is None:
            return

        if reponse and not self._sauvegarder():
            messagebox.showerror(
                "Sauvegarde",
                "Impossible de sauvegarder les données.",
                parent=self,
            )
            return

        self.destroy()

    def afficher_ecran(self, nom: str) -> None:
        if nom not in ECRANS:
            nom = "livres"

        if self.ecran_actuel is not None:
            self.ecran_actuel.destroy()

        if nom == "livres":
            self.ecran_actuel = EcranPrincipal(
                self.conteneur,
                self.bibliotheque,
                self.erreur_chargement,
                on_mutation=self._apres_mutation,
                on_sauvegarder=self._sauvegarder,
                on_backup=self._creer_backup,
            )
        else:
            self.ecran_actuel = EcranUtilisateurs(
                self.conteneur,
                self.bibliotheque,
                self.erreur_chargement,
                on_mutation=self._apres_mutation,
            )

        self.ecran_actuel.pack(fill="both", expand=True)
        self._mettre_a_jour_navigation(nom)
        self._mettre_a_jour_statistiques()

    def _mettre_a_jour_navigation(self, nom_actif: str) -> None:
        for nom, bouton in self.boutons_navigation.items():
            actif = nom == nom_actif
            bouton.configure(
                fg_color=COULEUR_ACTIF if actif else "transparent",
                hover_color=COULEUR_ACTIF if actif else COULEUR_SURVOL,
                text_color=COULEUR_TEXTE_ACTIF if actif else COULEUR_TEXTE_MENU,
                font=POLICE_NAV_ACTIVE if actif else POLICE_NAV,
            )


def main() -> None:
    analyseur = argparse.ArgumentParser(
        description="Système de gestion de bibliothèque",
    )
    analyseur.add_argument(
        "-d",
        "--data-dir",
        default=str(REPERTOIRE_DONNEES),
        help="répertoire contenant books.txt et users.txt",
    )
    arguments = analyseur.parse_args()

    repertoire_donnees = Path(arguments.data_dir)
    if not repertoire_donnees.is_dir():
        raise SystemExit(
            f"Erreur : le répertoire {repertoire_donnees} n'existe pas."
        )

    application = Application(repertoire_donnees)
    application.mainloop()


if __name__ == "__main__":
    main()
