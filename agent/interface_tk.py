"""Interface Tkinter complète du système de gestion de bibliothèque."""

import sys
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

CHEMIN_BUILD = Path(__file__).resolve().parent / "build"
sys.path.insert(0, str(CHEMIN_BUILD))
try:
    import bibliotheque_py as bibliotheque
except ImportError as exc:
    raise SystemExit(
        "Module bibliotheque_py introuvable. Construisez-le avec :\n"
        'cmake -S agent -B agent/build -Dpybind11_DIR="$(python3 -m pybind11 --cmakedir)" '
        "&& cmake --build agent/build"
    ) from exc

DONNEES = Path(__file__).resolve().parent / "data"

COULEURS = {
    "fond": "#f5f5f5",
    "menu": "#ecf0f1",
    "entete": "#2c3e50",
    "texte": "#2c3e50",
    "gris": "#7f8c8d",
    "bleu": "#3498db",
    "bleu_clair": "#d6eaf8",
    "vert": "#27ae60",
    "rouge": "#c0392b",
    "bordure": "#d5d9e0",
    "statut": "#bdbdbd",
}

MENU = (
    ("LIVRES", (
        ("ajouter_livre", "Ajouter un livre"),
        ("supprimer_livre", "Supprimer un livre"),
        ("rechercher_titre", "Rechercher par titre"),
        ("rechercher_auteur", "Rechercher par auteur"),
        ("tous_les_livres", "Tous les livres"),
        ("livres_disponibles", "Livres disponibles"),
    )),
    ("UTILISATEURS", (
        ("ajouter_utilisateur", "Ajouter un utilisateur"),
        ("tous_les_utilisateurs", "Tous les utilisateurs"),
    )),
    ("EMPRUNTS", (
        ("emprunter_livre", "Emprunter un livre"),
        ("retourner_livre", "Retourner un livre"),
    )),
    ("DONNEES", (
        ("statistiques", "Statistiques"),
        ("sauvegarder", "Sauvegarder"),
        ("creer_sauvegarde", "Créer une sauvegarde"),
    )),
)

TITRES_PAGES = {
    "ajouter_livre": "Ajouter un livre",
    "supprimer_livre": "Supprimer un livre",
    "rechercher_titre": "Rechercher par titre",
    "rechercher_auteur": "Rechercher par auteur",
    "tous_les_livres": "Tous les livres",
    "livres_disponibles": "Livres disponibles",
    "ajouter_utilisateur": "Ajouter un utilisateur",
    "tous_les_utilisateurs": "Tous les utilisateurs",
    "emprunter_livre": "Emprunter un livre",
    "retourner_livre": "Retourner un livre",
    "statistiques": "Statistiques de la bibliothèque",
    "sauvegarder": "Sauvegarder les données",
    "creer_sauvegarde": "Créer une sauvegarde",
}

PAGES_LIVRES = {
    "ajouter_livre", "supprimer_livre", "rechercher_titre", "rechercher_auteur",
    "tous_les_livres", "livres_disponibles",
}

PAGES_UTILISATEURS = {"ajouter_utilisateur", "tous_les_utilisateurs"}
PAGES_EMPRUNTS = {"emprunter_livre", "retourner_livre"}

TITRE_RECHERCHE = "Rechercher un titre, un auteur..."


def choisir_police(*candidates):
    familles = tkfont.families()
    return next((famille for famille in candidates if famille in familles), "DejaVu Sans")


class BibliothequeUI:
    def __init__(self, root, data_dir=DONNEES):
        self.root = root
        self.root.title("Gestion de Bibliothèque Personnelle")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 650)
        self.root.configure(bg=COULEURS["fond"])
        self.root.protocol("WM_DELETE_WINDOW", self._fermer)

        self.data_dir = Path(data_dir)
        self.session = bibliotheque.LibrarySession(str(self.data_dir))
        self.tableau = None

        famille = choisir_police("Segoe UI", "DejaVu Sans")
        self.police = (famille, 10)
        self.police_petite = (famille, 9)
        self.police_gras = (famille, 10, "bold")
        self.police_titre = (famille, 14, "bold")
        self.police_entete = (famille, 15, "bold")
        self.police_chiffre = (famille, 24, "bold")

        self.items_menu = {}
        self._configurer_styles()
        self._creer_entete()
        self._creer_barre_statut()
        self._creer_corps()
        self.afficher_page("tous_les_livres")

    def _configurer_styles(self):
        style = ttk.Style()
        style.configure(
            "Bibliotheque.Treeview",
            background="white",
            fieldbackground="white",
            foreground=COULEURS["texte"],
            rowheight=34,
            font=self.police,
        )
        style.configure(
            "Bibliotheque.Treeview.Heading",
            background=COULEURS["bordure"],
            foreground="#34495e",
            font=self.police_gras,
            relief="flat",
        )
        style.map(
            "Bibliotheque.Treeview",
            background=[("selected", COULEURS["bleu_clair"])],
            foreground=[("selected", COULEURS["texte"])],
        )

    def _creer_entete(self):
        entete = tk.Frame(self.root, bg=COULEURS["entete"], height=62)
        entete.pack(side="top", fill="x")
        entete.pack_propagate(False)
        tk.Label(
            entete,
            text="SYSTÈME DE GESTION DE BIBLIOTHÈQUE PERSONNELLE",
            bg=COULEURS["entete"],
            fg="white",
            font=self.police_entete,
        ).pack(side="left", padx=25)

    def _creer_barre_statut(self):
        barre = tk.Frame(self.root, bg=COULEURS["statut"], height=26)
        barre.pack(side="bottom", fill="x")
        barre.pack_propagate(False)
        self.statut_label = tk.Label(
            barre, text="", bg=COULEURS["statut"],
            fg=COULEURS["texte"], font=self.police_petite,
        )
        self.statut_label.pack(side="left", padx=12)

    def _creer_corps(self):
        corps = tk.Frame(self.root, bg=COULEURS["fond"])
        corps.pack(side="top", fill="both", expand=True)
        self._creer_menu(corps)
        contenu = tk.Frame(corps, bg=COULEURS["fond"])
        contenu.pack(side="left", fill="both", expand=True)
        self.titre_label = tk.Label(
            contenu, text="", bg=COULEURS["fond"], fg=COULEURS["texte"],
            font=self.police_titre, anchor="w",
        )
        self.titre_label.pack(side="top", fill="x", padx=28, pady=(12, 48))
        self.message_label = tk.Label(
            contenu, text="", bg=COULEURS["fond"], fg=COULEURS["gris"],
            font=self.police_petite, anchor="w",
        )
        self.message_label.pack(side="bottom", fill="x", padx=28, pady=(0, 10))
        self.page = tk.Frame(contenu, bg=COULEURS["fond"])
        self.page.pack(side="top", fill="both", expand=True, padx=28)

    def _section(self, parent, titre):
        tk.Label(
            parent, text=titre, bg=COULEURS["menu"], fg=COULEURS["gris"],
            font=self.police_petite + ("bold",), anchor="w",
        ).pack(fill="x", padx=18, pady=(11, 3))

    def _item(self, parent, texte, cle):
        label = tk.Label(
            parent, text=texte, bg=COULEURS["menu"], fg=COULEURS["texte"],
            font=self.police, anchor="w", padx=22, pady=6, cursor="hand2",
        )
        label.bind("<Button-1>", lambda _event, c=cle: self.afficher_page(c))
        label.pack(fill="x")
        self.items_menu[cle] = label

    def _creer_menu(self, parent):
        menu = tk.Frame(parent, bg=COULEURS["menu"], width=250)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)
        for titre_section, entrees in MENU:
            self._section(menu, titre_section)
            for cle, texte in entrees:
                self._item(menu, texte, cle)

    def afficher_page(self, cle):
        titre = TITRES_PAGES[cle]
        for cle_item, label in self.items_menu.items():
            actif = cle_item == cle
            label.config(
                bg=COULEURS["bleu"] if actif else COULEURS["menu"],
                fg="white" if actif else COULEURS["texte"],
            )
        self.titre_label.config(text=titre)
        self.statut_label.config(text=titre)
        self._message("")
        self.tableau = None
        for enfant in self.page.winfo_children():
            enfant.destroy()
        getattr(self, "_page_" + cle)()
        if cle in PAGES_LIVRES:
            self._maj_statut_livres()
        elif cle in PAGES_UTILISATEURS:
            self._maj_statut_utilisateurs()
        elif cle in PAGES_EMPRUNTS:
            self._maj_statut_emprunts()

    def _message(self, texte, genre="info"):
        couleurs = {
            "info": COULEURS["gris"],
            "succes": COULEURS["vert"],
            "erreur": COULEURS["rouge"],
        }
        self.message_label.config(text=texte, fg=couleurs[genre])

    def _maj_statut_livres(self):
        stats = self.session.stats()
        self.statut_label.config(
            text=f"Tous les livres  |  {stats['total_books']} livres  "
                 f"|  {stats['available_books']} disponibles"
        )

    def _maj_statut_utilisateurs(self):
        total = self.session.stats()["total_users"]
        self.statut_label.config(
            text=f"Utilisateurs  |  {total} utilisateur(s) enregistré(s)"
        )

    def _maj_statut_emprunts(self):
        stats = self.session.stats()
        self.statut_label.config(
            text=f"Emprunts  |  {stats['checked_out_books']} livre(s) emprunté(s)  "
                 f"|  {stats['available_books']} disponibles"
        )

    def _nouvelle_entree(self, parent, placeholder=""):
        entree = tk.Entry(
            parent, font=self.police, bg="white", relief="solid", bd=1,
            highlightthickness=0,
        )
        if placeholder:
            entree.insert(0, placeholder)
            entree.config(fg=COULEURS["gris"])
            entree.bind(
                "<FocusIn>",
                lambda _event, w=entree: self._effacer_placeholder(w, placeholder),
            )
            entree.bind(
                "<FocusOut>",
                lambda _event, w=entree: self._restaurer_placeholder(w, placeholder),
            )
        return entree

    @staticmethod
    def _effacer_placeholder(entree, placeholder):
        if entree.get() == placeholder:
            entree.delete(0, "end")
            entree.config(fg=COULEURS["texte"])

    @staticmethod
    def _restaurer_placeholder(entree, placeholder):
        if not entree.get().strip():
            entree.delete(0, "end")
            entree.insert(0, placeholder)
            entree.config(fg=COULEURS["gris"])

    def _lire(self, entree, placeholder=""):
        texte = entree.get().strip()
        return "" if texte == placeholder else texte

    @staticmethod
    def _reinitialiser(*champs):
        for entree, placeholder in champs:
            BibliothequeUI._restaurer_placeholder(entree, placeholder)

    def _persister(self):
        if self.session.save():
            return True
        self._message(
            "Erreur lors de la sauvegarde des données de la bibliothèque.",
            "erreur",
        )
        return False

    def _champ(self, parent, libelle, placeholder=""):
        ligne = tk.Frame(parent, bg=COULEURS["fond"])
        ligne.pack(fill="x", pady=7)
        tk.Label(
            ligne, text=libelle, width=16, anchor="w",
            bg=COULEURS["fond"], fg=COULEURS["texte"], font=self.police_gras,
        ).pack(side="left")
        entree = self._nouvelle_entree(ligne, placeholder)
        entree.pack(side="left", fill="x", expand=True, ipady=7)
        return entree

    def _bouton(self, parent, texte, couleur, largeur=16, active=None, command=None):
        return tk.Button(
            parent, text=texte, bg=couleur, fg="white",
            activebackground=active or couleur, activeforeground="white",
            relief="flat", font=self.police_gras, width=largeur, command=command,
        )

    def _actions(self, *boutons):
        cadre = tk.Frame(self.page, bg=COULEURS["fond"])
        cadre.pack(fill="x", pady=(42, 0))
        for texte, couleur, largeur, active, command in reversed(boutons):
            bouton = tk.Button(
                cadre, text=texte, bg=couleur, fg="white",
                activebackground=active or couleur, activeforeground="white",
                relief="flat", font=self.police_gras, width=largeur,
                cursor="hand2", command=command,
            )
            bouton.pack(side="right", padx=(12, 0), ipady=8)
        return cadre

    def _colonne_livres(self):
        return (
            ("id", "ISBN", 140),
            ("titre", "Titre", 280),
            ("auteur", "Auteur", 260),
            ("statut", "Statut", 200),
        )

    @staticmethod
    def _lignes_livres(livres):
        return [
            (livre.isbn, livre.title, livre.author,
             "Disponible" if livre.available else "Emprunté")
            for livre in livres
        ]

    def _tableau(self, colonnes, lignes, selection=None, hauteur=7):
        tableau = ttk.Treeview(
            self.page, columns=[c[0] for c in colonnes], show="headings",
            style="Bibliotheque.Treeview", height=hauteur, selectmode="browse",
        )
        for cle, titre, largeur in colonnes:
            tableau.heading(cle, text=titre, anchor="w")
            tableau.column(cle, width=largeur, anchor="w", stretch=False)
        tableau.tag_configure("disponible", foreground=COULEURS["vert"])
        tableau.tag_configure("emprunte", foreground=COULEURS["rouge"])
        self.tableau = tableau
        self._remplir_tableau(lignes, selection)
        tableau.pack(fill="x", pady=(18, 0))
        return tableau

    def _remplir_tableau(self, lignes, selection=None):
        for item in self.tableau.get_children():
            self.tableau.delete(item)
        for values in lignes:
            tag = None
            if values[-1] == "Disponible":
                tag = "disponible"
            elif values[-1] == "Emprunté":
                tag = "emprunte"
            self.tableau.insert(
                "", "end", iid=values[0], values=values,
                tags=(tag,) if tag else (),
            )
        if selection:
            self.tableau.selection_set(selection)
            self.tableau.focus(selection)

    def _panneau(self, titre, lignes):
        cadre = tk.Frame(
            self.page, bg="white",
            highlightbackground=COULEURS["bordure"], highlightthickness=1,
        )
        cadre.pack(fill="x", pady=(8, 0))
        tk.Label(
            cadre, text=titre, bg="white", fg=COULEURS["texte"],
            font=self.police_gras, anchor="w",
        ).pack(fill="x", padx=18, pady=(16, 8))
        etiquettes = []
        for ligne in lignes:
            etiquette = tk.Label(
                cadre, text=ligne, bg="white", fg=COULEURS["gris"],
                font=self.police, anchor="w", justify="left",
            )
            etiquette.pack(fill="x", padx=18, pady=3)
            etiquettes.append(etiquette)
        tk.Frame(cadre, height=14, bg="white").pack(fill="x")
        return cadre, etiquettes

    def _page_tous_les_livres(self):
        recherche = tk.Frame(self.page, bg=COULEURS["fond"])
        recherche.pack(fill="x")
        self.entree_recherche = self._nouvelle_entree(recherche, TITRE_RECHERCHE)
        self.entree_recherche.pack(side="left", fill="x", expand=True, ipady=8)
        self.entree_recherche.bind("<Return>", lambda _event: self._rechercher_global())
        self._bouton(
            recherche, "Rechercher", COULEURS["bleu"], 12, "#2980b9",
            self._rechercher_global,
        ).pack(side="left", padx=(8, 0), ipady=8)
        self._tableau(
            self._colonne_livres(),
            self._lignes_livres(self.session.get_all_books()),
        )
        self._actions(
            (
                "Emprunter", COULEURS["vert"], 14, "#229954",
                lambda: self.afficher_page("emprunter_livre"),
            ),
            (
                "Supprimer", COULEURS["rouge"], 13, "#a93226",
                self._supprimer_selection,
            ),
        )

    def _page_livres_disponibles(self):
        livres = self.session.get_available_books()
        self._panneau(
            f"{len(livres)} livres peuvent être empruntés",
            ["La liste ci-dessous présente uniquement les livres actuellement disponibles."],
        )
        self._tableau(self._colonne_livres(), self._lignes_livres(livres))

    def _page_ajouter_livre(self):
        self.entree_titre = self._champ(self.page, "Titre", "Entrez le titre du livre")
        self.entree_auteur = self._champ(self.page, "Auteur", "Entrez l'auteur du livre")
        self.entree_isbn = self._champ(self.page, "ISBN", "Entrez l'ISBN du livre")
        self._actions((
            "Ajouter le livre", COULEURS["bleu"], 16, "#2980b9",
            self._ajouter_livre,
        ))

    def _page_supprimer_livre(self):
        self.entree_isbn_supprimer = self._champ(
            self.page, "ISBN", "Entrez l'ISBN du livre à supprimer",
        )
        self._actions((
            "Supprimer le livre", COULEURS["rouge"], 16, "#a93226",
            self._supprimer_livre,
        ))
        self._tableau(
            self._colonne_livres(),
            self._lignes_livres(self.session.get_all_books()),
        )

    def _page_rechercher_titre(self):
        self.entree_recherche_titre = self._champ(
            self.page, "Titre", "Entrez le titre à rechercher",
        )
        self.entree_recherche_titre.bind(
            "<Return>", lambda _event: self._rechercher_titre(),
        )
        self._actions((
            "Rechercher", COULEURS["bleu"], 16, "#2980b9",
            self._rechercher_titre,
        ))
        self._tableau(
            self._colonne_livres(),
            self._lignes_livres(self.session.get_all_books()),
        )

    def _page_rechercher_auteur(self):
        self.entree_recherche_auteur = self._champ(
            self.page, "Auteur", "Entrez l'auteur à rechercher",
        )
        self.entree_recherche_auteur.bind(
            "<Return>", lambda _event: self._rechercher_auteur(),
        )
        self._actions((
            "Rechercher", COULEURS["bleu"], 16, "#2980b9",
            self._rechercher_auteur,
        ))
        self._tableau(
            self._colonne_livres(),
            self._lignes_livres(self.session.get_all_books()),
        )

    def _page_ajouter_utilisateur(self):
        self.entree_nom = self._champ(
            self.page, "Nom", "Entrez le nom de l'utilisateur",
        )
        self.entree_id_utilisateur = self._champ(
            self.page, "ID", "Entrez l'ID de l'utilisateur",
        )
        self.entree_id_utilisateur.bind(
            "<Return>", lambda _event: self._ajouter_utilisateur(),
        )
        self._actions((
            "Ajouter l'utilisateur", COULEURS["bleu"], 18, "#2980b9",
            self._ajouter_utilisateur,
        ))

    def _page_tous_les_utilisateurs(self):
        colonnes = (
            ("id", "ID", 200),
            ("nom", "Nom", 360),
            ("livres", "Livres empruntés", 320),
        )
        lignes = [
            (u.user_id, u.name, ", ".join(u.borrowed_books))
            for u in self.session.get_all_users()
        ]
        self._tableau(colonnes, lignes)

    def _page_emprunter_livre(self):
        self.entree_isbn_emprunt = self._champ(
            self.page, "ISBN", "Entrez l'ISBN du livre à emprunter",
        )
        self.entree_id_emprunt = self._champ(
            self.page, "ID utilisateur", "Entrez l'ID de l'utilisateur",
        )
        self.entree_id_emprunt.bind(
            "<Return>", lambda _event: self._emprunter_livre(),
        )
        self._actions((
            "Emprunter", COULEURS["vert"], 16, "#229954",
            self._emprunter_livre,
        ))
        self._tableau(
            self._colonne_livres(),
            self._lignes_livres(self.session.get_available_books()),
        )

    def _page_retourner_livre(self):
        self.entree_isbn_retour = self._champ(
            self.page, "ISBN", "Entrez l'ISBN du livre à retourner",
        )
        self.entree_isbn_retour.bind(
            "<Return>", lambda _event: self._retourner_livre(),
        )
        self._actions((
            "Retourner le livre", COULEURS["vert"], 16, "#229954",
            self._retourner_livre,
        ))
        self._tableau(
            self._colonne_livres(),
            self._lignes_livres([
                livre for livre in self.session.get_all_books()
                if not livre.available
            ]),
        )

    def _page_statistiques(self):
        cartes = tk.Frame(self.page, bg=COULEURS["fond"])
        cartes.pack(fill="x")
        stats = self.session.stats()
        donnees = (
            ("Total des livres", stats["total_books"], COULEURS["bleu"]),
            ("Livres disponibles", stats["available_books"], COULEURS["vert"]),
            ("Livres empruntés", stats["checked_out_books"], COULEURS["rouge"]),
            ("Total des utilisateurs", stats["total_users"], COULEURS["entete"]),
        )
        for index, (titre, valeur, couleur) in enumerate(donnees):
            carte = tk.Frame(
                cartes, bg="white",
                highlightbackground=COULEURS["bordure"], highlightthickness=1,
            )
            carte.pack(side="left", fill="both", expand=True, padx=(0 if index == 0 else 12, 0))
            tk.Label(
                carte, text=titre, bg="white", fg=COULEURS["gris"],
                font=self.police_petite, anchor="w",
            ).pack(fill="x", padx=16, pady=(16, 2))
            tk.Label(
                carte, text=str(valeur), bg="white", fg=couleur,
                font=self.police_chiffre, anchor="w",
            ).pack(fill="x", padx=16, pady=(0, 18))

    def _page_sauvegarder(self):
        _cadre, etiquettes = self._panneau(
            "Sauvegarde des données",
            [
                "Les fichiers books.txt et users.txt seront enregistrés dans le dossier de données.",
                "Dernière sauvegarde : aucune dans cette session.",
            ],
        )
        self.etiquette_derniere_sauvegarde = etiquettes[1]
        self._actions((
            "Sauvegarder", COULEURS["bleu"], 16, "#2980b9",
            self._sauvegarder,
        ))

    def _page_creer_sauvegarde(self):
        _cadre, etiquettes = self._panneau(
            "Copie de sécurité",
            [
                "Crée books.txt.backup et users.txt.backup à côté des fichiers de données.",
                "Une sauvegarde existante est remplacée automatiquement.",
            ],
        )
        self.etiquette_derniere_copie = etiquettes[1]
        self._actions((
            "Créer une sauvegarde", COULEURS["vert"], 18, "#229954",
            self._creer_sauvegarde,
        ))

    def _rechercher_global(self):
        texte = self._lire(self.entree_recherche, TITRE_RECHERCHE)
        if not texte:
            livres = self.session.get_all_books()
        else:
            trouves = {}
            for livre in (
                self.session.search_books_by_title(texte)
                + self.session.search_books_by_author(texte)
            ):
                trouves[livre.isbn] = livre
            livres = list(trouves.values())
        self._remplir_tableau(self._lignes_livres(livres))
        self._message(f"{len(livres)} livre(s) trouvé(s).")

    def _rechercher_titre(self):
        texte = self._lire(
            self.entree_recherche_titre, "Entrez le titre à rechercher",
        )
        if not texte:
            self._message("Erreur : Entrez le titre à rechercher.", "erreur")
            return
        livres = self.session.search_books_by_title(texte)
        self._remplir_tableau(self._lignes_livres(livres))
        if livres:
            self._message(f"{len(livres)} livre(s) trouvé(s).", "succes")
        else:
            self._message("Aucun livre trouvé avec ce titre.", "erreur")

    def _rechercher_auteur(self):
        texte = self._lire(
            self.entree_recherche_auteur, "Entrez l'auteur à rechercher",
        )
        if not texte:
            self._message("Erreur : Entrez l'auteur à rechercher.", "erreur")
            return
        livres = self.session.search_books_by_author(texte)
        self._remplir_tableau(self._lignes_livres(livres))
        if livres:
            self._message(f"{len(livres)} livre(s) trouvé(s).", "succes")
        else:
            self._message("Aucun livre trouvé de cet auteur.", "erreur")

    def _ajouter_livre(self):
        titre = self._lire(self.entree_titre, "Entrez le titre du livre")
        auteur = self._lire(self.entree_auteur, "Entrez l'auteur du livre")
        isbn = self._lire(self.entree_isbn, "Entrez l'ISBN du livre")
        if not (titre and auteur and isbn):
            self._message("Erreur : Tous les champs sont obligatoires.", "erreur")
            return
        if not self.session.add_book(titre, auteur, isbn):
            self._message(
                f"Erreur : Un livre avec l'ISBN {isbn} existe déjà.", "erreur",
            )
            return
        if not self._persister():
            return
        self._message("Livre ajouté avec succès !", "succes")
        self._reinitialiser(
            (self.entree_titre, "Entrez le titre du livre"),
            (self.entree_auteur, "Entrez l'auteur du livre"),
            (self.entree_isbn, "Entrez l'ISBN du livre"),
        )
        self._maj_statut_livres()

    def _supprimer_livre(self):
        isbn = self._lire(
            self.entree_isbn_supprimer, "Entrez l'ISBN du livre à supprimer",
        )
        if not isbn:
            self._message("Erreur : Entrez l'ISBN du livre à supprimer.", "erreur")
            return
        self._supprimer(isbn, self.entree_isbn_supprimer)

    def _supprimer_selection(self):
        selection = self.tableau.selection()
        if not selection:
            self._message("Erreur : Sélectionnez un livre à supprimer.", "erreur")
            return
        self._supprimer(self.tableau.item(selection[0], "values")[0])

    def _supprimer(self, isbn, entree=None):
        if not self.session.remove_book(isbn):
            self._message("Livre non trouvé.", "erreur")
            return
        if not self._persister():
            return
        self._message("Livre supprimé avec succès !", "succes")
        if entree is not None:
            self._restaurer_placeholder(entree, "Entrez l'ISBN du livre à supprimer")
        self._remplir_tableau(self._lignes_livres(self.session.get_all_books()))
        self._maj_statut_livres()

    def _ajouter_utilisateur(self):
        nom = self._lire(self.entree_nom, "Entrez le nom de l'utilisateur")
        identifiant = self._lire(
            self.entree_id_utilisateur, "Entrez l'ID de l'utilisateur",
        )
        if not (nom and identifiant):
            self._message("Erreur : Tous les champs sont obligatoires.", "erreur")
            return
        if not self.session.add_user(nom, identifiant):
            self._message(
                f"Erreur : Un utilisateur avec l'ID {identifiant} existe déjà.",
                "erreur",
            )
            return
        if not self._persister():
            return
        self._reinitialiser(
            (self.entree_nom, "Entrez le nom de l'utilisateur"),
            (self.entree_id_utilisateur, "Entrez l'ID de l'utilisateur"),
        )
        self.afficher_page("tous_les_utilisateurs")
        self._message(
            f"Utilisateur {nom} ({identifiant}) ajouté avec succès !", "succes",
        )

    def _emprunter_livre(self):
        isbn = self._lire(
            self.entree_isbn_emprunt, "Entrez l'ISBN du livre à emprunter",
        )
        identifiant = self._lire(
            self.entree_id_emprunt, "Entrez l'ID de l'utilisateur",
        )
        if not (isbn and identifiant):
            self._message("Erreur : Tous les champs sont obligatoires.", "erreur")
            return
        if not self.session.check_out_book(isbn, identifiant):
            self._message(
                "Erreur : Impossible d'emprunter le livre. Vérifiez l'ISBN, "
                "l'ID utilisateur et la disponibilité du livre.",
                "erreur",
            )
            return
        if not self._persister():
            return
        self._message("Livre emprunté avec succès !", "succes")
        self._reinitialiser(
            (self.entree_isbn_emprunt, "Entrez l'ISBN du livre à emprunter"),
            (self.entree_id_emprunt, "Entrez l'ID de l'utilisateur"),
        )
        self._remplir_tableau(
            self._lignes_livres(self.session.get_available_books())
        )
        self._maj_statut_emprunts()

    def _retourner_livre(self):
        isbn = self._lire(
            self.entree_isbn_retour, "Entrez l'ISBN du livre à retourner",
        )
        if not isbn:
            self._message("Erreur : Entrez l'ISBN du livre à retourner.", "erreur")
            return
        if not self.session.return_book(isbn):
            self._message(
                "Erreur : Impossible de retourner le livre. Vérifiez l'ISBN "
                "et que le livre est bien emprunté.",
                "erreur",
            )
            return
        if not self._persister():
            return
        self._message("Livre retourné avec succès !", "succes")
        self._reinitialiser(
            (self.entree_isbn_retour, "Entrez l'ISBN du livre à retourner"),
        )
        self._remplir_tableau(self._lignes_livres([
            livre for livre in self.session.get_all_books()
            if not livre.available
        ]))
        self._maj_statut_emprunts()

    def _sauvegarder(self):
        if self.session.save():
            horaire = datetime.now().strftime("%H:%M:%S")
            self.etiquette_derniere_sauvegarde.config(
                text=f"Dernière sauvegarde : {horaire}"
            )
            self._message(
                "Données de la bibliothèque sauvegardées avec succès !", "succes",
            )
        else:
            self._message(
                "Erreur lors de la sauvegarde des données de la bibliothèque.",
                "erreur",
            )

    def _creer_sauvegarde(self):
        for nom in ("books.txt.backup", "users.txt.backup"):
            chemin = self.data_dir / nom
            if chemin.exists():
                chemin.unlink()
        self.session.save()
        if self.session.backup():
            horaire = datetime.now().strftime("%H:%M:%S")
            self.etiquette_derniere_copie.config(
                text=f"Dernière copie de sécurité : {horaire}"
            )
            self._message("Fichiers de sauvegarde créés.", "succes")
        else:
            self._message(
                "Erreur : Impossible de créer la sauvegarde.", "erreur",
            )

    def _fermer(self):
        self.session.save()
        self.root.destroy()


def main():
    racine = tk.Tk()
    BibliothequeUI(racine)
    racine.mainloop()


if __name__ == "__main__":
    main()
