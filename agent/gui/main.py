"""Interface graphique rose de gestion de bibliothèque.

Les sources C++ d'origine ne sont pas modifiées : toutes les opérations
passent par le module pybind11 _cpp_backend défini dans cpp/backend.cpp.
"""

import sys
from pathlib import Path
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

sys.path.insert(0, str(Path(__file__).resolve().parent / "build"))

import _cpp_backend  # noqa: E402  (le chemin du module doit être ajouté avant)

# Palette rose définie ici volontairement : aucun fichier de thème externe.
ROSE_FOND = "#FFF0F5"
ROSE_PALE = "#FFF5F8"
ROSE_CARTE = "#FCE4EC"
ROSE_LEGER = "#F8BBD0"
ROSE_ACCENT = "#E75480"
ROSE_FONCE = "#C9184A"
ROSE_TEXTE = "#4A1C2E"
VERT = "#2E7D5B"
BLANC = "#FFFFFF"

DOSSIER_DONNEES = Path(__file__).resolve().parent / "data"
FICHIER_LIVRES = DOSSIER_DONNEES / "books.txt"
FICHIER_UTILISATEURS = DOSSIER_DONNEES / "users.txt"

STYLE_ENTRY = {
    "fg_color": ROSE_PALE,
    "border_color": ROSE_LEGER,
    "text_color": ROSE_TEXTE,
    "corner_radius": 10,
}
STYLE_BOUTON = {
    "fg_color": ROSE_ACCENT,
    "hover_color": ROSE_FONCE,
    "text_color": BLANC,
    "corner_radius": 10,
}


def preparer_donnees() -> None:
    """Crée le dossier et les fichiers de données s'ils n'existent pas."""
    DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)
    for fichier in (FICHIER_LIVRES, FICHIER_UTILISATEURS):
        if not fichier.exists():
            fichier.touch()


class BibliothequeApp(ctk.CTk):
    """Fenêtre principale : formulaires à gauche, listes à droite."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Bibliothèque Rose")
        self.geometry("1120x720")
        self.minsize(960, 640)
        self.configure(fg_color=ROSE_FOND)

        preparer_donnees()
        self.bibliotheque = _cpp_backend.Library()
        self.gestionnaire = _cpp_backend.FileManager(
            str(FICHIER_LIVRES), str(FICHIER_UTILISATEURS)
        )
        self.gestionnaire.loadLibraryData(self.bibliotheque)

        self._construire_interface()
        self.actualiser_tout()
        self.protocol("WM_DELETE_WINDOW", self.quitter)

    # ------------------------------------------------------------------ UI

    def _construire_interface(self) -> None:
        # Barre inférieure (packée en premier pour réserver sa place).
        pied = ctk.CTkFrame(self, fg_color=ROSE_CARTE, corner_radius=0, height=58)
        pied.pack(side="bottom", fill="x")
        pied.pack_propagate(False)

        self.statut = ctk.CTkLabel(
            pied,
            text="Prêt",
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=ROSE_FONCE,
        )
        self.statut.pack(side="left", padx=18)

        for texte, commande in (
            ("Sauvegarder", self.sauvegarder),
            ("Créer une sauvegarde", self.creer_sauvegarde),
            ("Recharger", self.recharger),
            ("Quitter", self.quitter),
        ):
            ctk.CTkButton(
                pied,
                text=texte,
                command=commande,
                height=32,
                font=ctk.CTkFont(size=12),
                **STYLE_BOUTON,
            ).pack(side="right", padx=6, pady=12)

        # En-tête avec les statistiques.
        entete = ctk.CTkFrame(self, fg_color=ROSE_ACCENT, corner_radius=0, height=96)
        entete.pack(side="top", fill="x")
        entete.pack_propagate(False)

        ctk.CTkLabel(
            entete,
            text="Bibliothèque Rose",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=BLANC,
        ).pack(side="left", padx=24)

        cadre_stats = ctk.CTkFrame(entete, fg_color="transparent")
        cadre_stats.pack(side="right", padx=24)
        self.stats: dict[str, ctk.CTkLabel] = {}
        for cle, libelle in (
            ("total", "Livres"),
            ("disponibles", "Disponibles"),
            ("empruntes", "Empruntés"),
            ("utilisateurs", "Utilisateurs"),
        ):
            boite = ctk.CTkFrame(cadre_stats, fg_color=ROSE_FONCE, corner_radius=12)
            boite.pack(side="left", padx=5, pady=16)
            valeur = ctk.CTkLabel(
                boite,
                text="0",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=BLANC,
            )
            valeur.pack(padx=14, pady=(8, 0))
            ctk.CTkLabel(
                boite,
                text=libelle,
                font=ctk.CTkFont(size=11),
                text_color=ROSE_LEGER,
            ).pack(padx=14, pady=(0, 8))
            self.stats[cle] = valeur

        # Corps : panneau de formulaires + onglets.
        corps = ctk.CTkFrame(self, fg_color="transparent")
        corps.pack(fill="both", expand=True, padx=16, pady=12)
        corps.grid_columnconfigure(0, weight=0, minsize=320)
        corps.grid_columnconfigure(1, weight=1)
        corps.grid_rowconfigure(0, weight=1)

        panneau = ctk.CTkFrame(corps, fg_color=ROSE_CARTE, corner_radius=18)
        panneau.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._construire_formulaires(panneau)

        self.onglets = ctk.CTkTabview(
            corps,
            fg_color=ROSE_CARTE,
            corner_radius=18,
            segmented_button_fg_color=ROSE_LEGER,
            segmented_button_selected_color=ROSE_ACCENT,
            segmented_button_selected_hover_color=ROSE_FONCE,
            segmented_button_unselected_color="#FADADD",
            segmented_button_unselected_hover_color=ROSE_LEGER,
            text_color=ROSE_TEXTE,
        )
        self.onglets.grid(row=0, column=1, sticky="nsew")

        self.listes: dict[str, ctk.CTkScrollableFrame] = {}
        for nom in ("Livres", "Disponibles", "Utilisateurs"):
            self.onglets.add(nom)
            onglet = self.onglets.tab(nom)
            onglet.grid_columnconfigure(0, weight=1)
            onglet.grid_rowconfigure(0, weight=1)
            liste = ctk.CTkScrollableFrame(onglet, fg_color=ROSE_FOND, corner_radius=12)
            liste.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
            self.listes[nom] = liste

        self.onglets.add("Recherche")
        onglet_recherche = self.onglets.tab("Recherche")
        onglet_recherche.grid_columnconfigure(0, weight=1)
        onglet_recherche.grid_rowconfigure(1, weight=1)

        barre = ctk.CTkFrame(onglet_recherche, fg_color="transparent")
        barre.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        self.champ_recherche = ctk.CTkEntry(
            barre, placeholder_text="Titre ou auteur…", **STYLE_ENTRY
        )
        self.champ_recherche.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            barre, text="Par titre", command=lambda: self.rechercher("titre"), **STYLE_BOUTON
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            barre, text="Par auteur", command=lambda: self.rechercher("auteur"), **STYLE_BOUTON
        ).pack(side="left", padx=4)

        self.liste_recherche = ctk.CTkScrollableFrame(
            onglet_recherche, fg_color=ROSE_FOND, corner_radius=12
        )
        self.liste_recherche.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _boite(self, parent: Any, titre: str) -> ctk.CTkFrame:
        boite = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=14)
        boite.pack(fill="x", padx=12, pady=8)
        ctk.CTkLabel(
            boite,
            text=titre,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ROSE_FONCE,
        ).pack(anchor="w", padx=14, pady=(12, 6))
        return boite

    def _construire_formulaires(self, parent: Any) -> None:
        ctk.CTkLabel(
            parent,
            text="Gestion de la bibliothèque",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=ROSE_FONCE,
        ).pack(anchor="w", padx=16, pady=(18, 4))

        livre = self._boite(parent, "Ajouter un livre")
        self.champ_titre = ctk.CTkEntry(livre, placeholder_text="Titre", **STYLE_ENTRY)
        self.champ_titre.pack(fill="x", padx=14, pady=3)
        self.champ_auteur = ctk.CTkEntry(livre, placeholder_text="Auteur", **STYLE_ENTRY)
        self.champ_auteur.pack(fill="x", padx=14, pady=3)
        self.champ_isbn = ctk.CTkEntry(livre, placeholder_text="ISBN", **STYLE_ENTRY)
        self.champ_isbn.pack(fill="x", padx=14, pady=3)
        ctk.CTkButton(
            livre, text="Ajouter le livre", command=self.ajouter_livre, **STYLE_BOUTON
        ).pack(fill="x", padx=14, pady=(8, 14))

        utilisateur = self._boite(parent, "Ajouter un utilisateur")
        self.champ_nom = ctk.CTkEntry(utilisateur, placeholder_text="Nom", **STYLE_ENTRY)
        self.champ_nom.pack(fill="x", padx=14, pady=3)
        self.champ_id = ctk.CTkEntry(utilisateur, placeholder_text="ID utilisateur", **STYLE_ENTRY)
        self.champ_id.pack(fill="x", padx=14, pady=3)
        ctk.CTkButton(
            utilisateur,
            text="Ajouter l'utilisateur",
            command=self.ajouter_utilisateur,
            **STYLE_BOUTON,
        ).pack(fill="x", padx=14, pady=(8, 14))

        emprunt = self._boite(parent, "Emprunter / retourner")
        self.champ_isbn_action = ctk.CTkEntry(emprunt, placeholder_text="ISBN", **STYLE_ENTRY)
        self.champ_isbn_action.pack(fill="x", padx=14, pady=3)
        self.champ_id_action = ctk.CTkEntry(
            emprunt, placeholder_text="ID utilisateur (emprunt)", **STYLE_ENTRY
        )
        self.champ_id_action.pack(fill="x", padx=14, pady=3)
        ligne_actions = ctk.CTkFrame(emprunt, fg_color="transparent")
        ligne_actions.pack(fill="x", padx=14, pady=(8, 14))
        ctk.CTkButton(
            ligne_actions, text="Emprunter", command=self.emprunter, **STYLE_BOUTON
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(
            ligne_actions, text="Retourner", command=self.retourner, **STYLE_BOUTON
        ).pack(side="right", fill="x", expand=True, padx=(4, 0))

    # -------------------------------------------------------------- Cartes

    @staticmethod
    def _vider(frame: Any) -> None:
        for widget in frame.winfo_children():
            widget.destroy()

    @staticmethod
    def _message_vide(frame: Any, texte: str) -> None:
        ctk.CTkLabel(
            frame, text=texte, font=ctk.CTkFont(size=13), text_color=ROSE_FONCE
        ).pack(padx=12, pady=20)

    def _carte_livre(self, parent: Any, livre: Any, supprimable: bool = False) -> None:
        carte = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=12)
        carte.pack(fill="x", padx=8, pady=6)

        disponible = livre.getAvailability()
        statut = "Disponible" if disponible else f"Emprunté par {livre.getBorrowerId()}"
        ctk.CTkLabel(
            carte,
            text=livre.getTitle(),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ROSE_FONCE,
        ).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(
            carte,
            text=f"{livre.getAuthor()}  •  ISBN {livre.getISBN()}",
            font=ctk.CTkFont(size=12),
            text_color=ROSE_TEXTE,
        ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkLabel(
            carte,
            text=statut,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=VERT if disponible else ROSE_FONCE,
        ).pack(anchor="w", padx=14, pady=(0, 10 if supprimable else 12))

        if supprimable:
            isbn = livre.getISBN()
            ctk.CTkButton(
                carte,
                text="Supprimer",
                width=90,
                height=26,
                font=ctk.CTkFont(size=11),
                command=lambda: self.supprimer_livre(isbn),
                fg_color=ROSE_FONCE,
                hover_color=ROSE_TEXTE,
                text_color=BLANC,
                corner_radius=8,
            ).pack(anchor="e", padx=14, pady=(0, 10))

    def _carte_utilisateur(self, parent: Any, utilisateur: Any) -> None:
        carte = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=12)
        carte.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(
            carte,
            text=utilisateur.getName(),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ROSE_FONCE,
        ).pack(anchor="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(
            carte,
            text=f"ID : {utilisateur.getUserId()}",
            font=ctk.CTkFont(size=12),
            text_color=ROSE_TEXTE,
        ).pack(anchor="w", padx=14, pady=2)
        livres = utilisateur.getBorrowedBooks()
        detail = ", ".join(livres) if livres else "Aucun livre emprunté"
        ctk.CTkLabel(
            carte,
            text=f"Emprunts ({utilisateur.getNumberOfBorrowedBooks()}) : {detail}",
            font=ctk.CTkFont(size=12),
            text_color=ROSE_TEXTE,
            wraplength=520,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(2, 12))

    # ------------------------------------------------------------ Mise à jour

    def actualiser_stats(self) -> None:
        self.stats["total"].configure(text=str(self.bibliotheque.getTotalBooks()))
        self.stats["disponibles"].configure(
            text=str(self.bibliotheque.getAvailableBookCount())
        )
        self.stats["empruntes"].configure(
            text=str(self.bibliotheque.getCheckedOutBookCount())
        )
        self.stats["utilisateurs"].configure(
            text=str(len(self.bibliotheque.getAllUsers()))
        )

    def actualiser_listes(self) -> None:
        for nom, frame in self.listes.items():
            self._vider(frame)
            if nom == "Utilisateurs":
                utilisateurs = self.bibliotheque.getAllUsers()
                if not utilisateurs:
                    self._message_vide(frame, "Aucun utilisateur enregistré.")
                for utilisateur in utilisateurs:
                    self._carte_utilisateur(frame, utilisateur)
                continue

            if nom == "Livres":
                livres = self.bibliotheque.getAllBooks()
                supprimable = True
                vide = "Aucun livre dans la bibliothèque."
            else:
                livres = self.bibliotheque.getAvailableBooks()
                supprimable = False
                vide = "Aucun livre disponible pour emprunt."

            if not livres:
                self._message_vide(frame, vide)
            for livre in livres:
                self._carte_livre(frame, livre, supprimable)

    def actualiser_tout(self) -> None:
        self.actualiser_stats()
        self.actualiser_listes()
        self._vider(self.liste_recherche)

    def dire(self, texte: str) -> None:
        self.statut.configure(text=texte)

    # -------------------------------------------------------------- Actions

    @staticmethod
    def _nettoyer(*champs: ctk.CTkEntry) -> None:
        for champ in champs:
            champ.delete(0, "end")

    def ajouter_livre(self) -> None:
        titre = self.champ_titre.get().strip()
        auteur = self.champ_auteur.get().strip()
        isbn = self.champ_isbn.get().strip()
        if not (titre and auteur and isbn):
            self.dire("Veuillez remplir le titre, l'auteur et l'ISBN.")
            return
        if self.bibliotheque.findBookByISBN(isbn) is not None:
            self.dire(f"Un livre avec l'ISBN {isbn} existe déjà.")
            return

        self.bibliotheque.addBook(_cpp_backend.Book(titre, auteur, isbn))
        self._nettoyer(self.champ_titre, self.champ_auteur, self.champ_isbn)
        self.dire(f"Livre « {titre} » ajouté.")
        self.actualiser_tout()

    def supprimer_livre(self, isbn: str) -> None:
        if not messagebox.askyesno("Confirmation", f"Supprimer le livre {isbn} ?"):
            return
        if self.bibliotheque.removeBook(isbn):
            self.dire(f"Livre {isbn} supprimé.")
            self.actualiser_tout()
        else:
            self.dire("Livre introuvable.")

    def ajouter_utilisateur(self) -> None:
        nom = self.champ_nom.get().strip()
        identifiant = self.champ_id.get().strip()
        if not (nom and identifiant):
            self.dire("Veuillez remplir le nom et l'ID de l'utilisateur.")
            return
        if self.bibliotheque.findUserById(identifiant) is not None:
            self.dire(f"Un utilisateur avec l'ID {identifiant} existe déjà.")
            return

        self.bibliotheque.addUser(_cpp_backend.User(nom, identifiant))
        self._nettoyer(self.champ_nom, self.champ_id)
        self.dire(f"Utilisateur « {nom} » ajouté.")
        self.actualiser_tout()

    def emprunter(self) -> None:
        isbn = self.champ_isbn_action.get().strip()
        identifiant = self.champ_id_action.get().strip()
        if not (isbn and identifiant):
            self.dire("Indiquez un ISBN et un ID utilisateur pour l'emprunt.")
            return
        if self.bibliotheque.checkOutBook(isbn, identifiant):
            self._nettoyer(self.champ_isbn_action, self.champ_id_action)
            self.dire(f"Livre {isbn} emprunté par {identifiant}.")
            self.actualiser_tout()
        else:
            self.dire("Emprunt impossible : vérifiez l'ISBN, l'ID et la disponibilité.")

    def retourner(self) -> None:
        isbn = self.champ_isbn_action.get().strip()
        if not isbn:
            self.dire("Indiquez l'ISBN du livre à retourner.")
            return
        if self.bibliotheque.returnBook(isbn):
            self._nettoyer(self.champ_isbn_action)
            self.dire(f"Livre {isbn} retourné.")
            self.actualiser_tout()
        else:
            self.dire("Retour impossible : vérifiez l'ISBN et l'emprunt.")

    def rechercher(self, critere: str) -> None:
        texte = self.champ_recherche.get().strip()
        self._vider(self.liste_recherche)
        self.onglets.set("Recherche")
        if not texte:
            self.dire("Entrez un titre ou un auteur à rechercher.")
            return

        if critere == "titre":
            livres = self.bibliotheque.searchBooksByTitle(texte)
        else:
            livres = self.bibliotheque.searchBooksByAuthor(texte)

        if not livres:
            self._message_vide(self.liste_recherche, "Aucun livre trouvé.")
        for livre in livres:
            self._carte_livre(self.liste_recherche, livre)
        self.dire(f"{len(livres)} résultat(s) pour « {texte} ».")

    def sauvegarder(self) -> None:
        if self.gestionnaire.saveLibraryData(self.bibliotheque):
            self.dire("Données sauvegardées.")
        else:
            self.dire("Erreur lors de la sauvegarde des données.")

    def creer_sauvegarde(self) -> None:
        try:
            self.gestionnaire.createBackup()
            self.dire("Fichiers de sauvegarde créés.")
        except Exception as erreur:
            self.dire(f"Impossible de créer la sauvegarde : {erreur}")

    def recharger(self) -> None:
        # Une nouvelle instance évite d'additionner les données déjà en mémoire.
        self.bibliotheque = _cpp_backend.Library()
        self.gestionnaire.loadLibraryData(self.bibliotheque)
        self.actualiser_tout()
        self.dire("Données rechargées depuis le disque.")

    def quitter(self) -> None:
        self.gestionnaire.saveLibraryData(self.bibliotheque)
        self.destroy()


def main() -> None:
    ctk.set_appearance_mode("light")
    application = BibliothequeApp()
    application.mainloop()


if __name__ == "__main__":
    main()
