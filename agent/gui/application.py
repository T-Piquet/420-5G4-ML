import customtkinter as ctk

from gui.controleur import ControleurBibliotheque


class VuePlaceholder(ctk.CTkFrame):
    def __init__(self, parent, titre: str):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(
            self,
            text=titre,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 8))
        ctk.CTkLabel(
            self,
            text="Composant en attente d'implémentation (étape 5).",
            text_color="gray",
        ).pack(anchor="w", padx=20)

    def rafraichir(self):
        pass


class ApplicationBibliotheque(ctk.CTk):
    SECTIONS = [
        ("tableau_bord", "Tableau de bord"),
        ("livres", "Livres"),
        ("utilisateurs", "Utilisateurs"),
        ("emprunts", "Emprunts"),
    ]

    def __init__(self, controleur: ControleurBibliotheque):
        super().__init__()
        self.controleur = controleur

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Gestion de Bibliothèque Personnelle")
        self.geometry("1050x680")
        self.minsize(850, 560)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.boutons_nav: dict[str, ctk.CTkButton] = {}
        self.vues: dict[str, ctk.CTkFrame] = {}
        self.section_active: str | None = None

        self._construire_barre_laterale()
        self._construire_zone_principale()
        self._construire_vues()

        self.afficher_section("tableau_bord")
        self.afficher_statut(
            f"Données chargées depuis {self.controleur.repertoire_donnees}"
        )

        self.protocol("WM_DELETE_WINDOW", self._fermer_application)

    def _construire_barre_laterale(self):
        self.barre_laterale = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.barre_laterale.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.barre_laterale.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            self.barre_laterale,
            text="Bibliothèque",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(24, 20), sticky="w")

        for index, (cle, libelle) in enumerate(self.SECTIONS, start=1):
            bouton = ctk.CTkButton(
                self.barre_laterale,
                text=libelle,
                anchor="w",
                height=38,
                command=lambda c=cle: self.afficher_section(c),
            )
            bouton.grid(row=index, column=0, padx=16, pady=6, sticky="ew")
            self.boutons_nav[cle] = bouton

        ctk.CTkLabel(
            self.barre_laterale,
            text="Apparence :",
            anchor="w",
        ).grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")

        self.menu_theme = ctk.CTkOptionMenu(
            self.barre_laterale,
            values=["Système", "Clair", "Sombre"],
            command=self._changer_theme,
        )
        self.menu_theme.grid(row=8, column=0, padx=16, pady=(6, 20), sticky="ew")

    def _construire_zone_principale(self):
        self.zone_contenu = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.zone_contenu.grid(row=0, column=1, sticky="nsew", padx=12, pady=(12, 6))
        self.zone_contenu.grid_columnconfigure(0, weight=1)
        self.zone_contenu.grid_rowconfigure(0, weight=1)

        self.barre_statut = ctk.CTkFrame(self, height=32, corner_radius=0)
        self.barre_statut.grid(row=1, column=1, sticky="ew")
        self.label_statut = ctk.CTkLabel(
            self.barre_statut,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
        )
        self.label_statut.pack(fill="x", padx=14, pady=4)

    def _construire_vues(self):
        for cle, libelle in self.SECTIONS:
            self.vues[cle] = VuePlaceholder(self.zone_contenu, libelle)

    def afficher_section(self, cle: str):
        if cle not in self.vues:
            return

        if self.section_active and self.section_active in self.vues:
            self.vues[self.section_active].grid_forget()

        self.section_active = cle
        vue = self.vues[cle]
        vue.grid(row=0, column=0, sticky="nsew")
        if hasattr(vue, "rafraichir"):
            vue.rafraichir()

        for k, bouton in self.boutons_nav.items():
            bouton.configure(
                fg_color=("gray75", "gray25") if k == cle else "transparent",
                text_color=("gray10", "gray90"),
            )

    def rafraichir_vue_active(self):
        if self.section_active and self.section_active in self.vues:
            vue = self.vues[self.section_active]
            if hasattr(vue, "rafraichir"):
                vue.rafraichir()

    def afficher_statut(self, message: str, succes: bool = True):
        couleur = ("#1b5e20", "#81c784") if succes else ("#b71c1c", "#ef9a9a")
        self.label_statut.configure(text=message, text_color=couleur)

    @staticmethod
    def _changer_theme(choix: str):
        correspondance = {
            "Système": "System",
            "Clair": "Light",
            "Sombre": "Dark",
        }
        ctk.set_appearance_mode(correspondance.get(choix, "System"))

    def _fermer_application(self):
        self.controleur.sauvegarder()
        self.destroy()
