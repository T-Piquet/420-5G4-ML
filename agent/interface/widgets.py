import tkinter as tk

import customtkinter as ctk

from . import theme


class NavBar(ctk.CTkFrame):
    def __init__(self, master, sur_changement):
        super().__init__(
            master,
            fg_color=theme.CARTE,
            corner_radius=0,
            border_width=1,
            border_color=theme.BORDURE,
            height=56,
        )
        self._sur_changement = sur_changement
        self._boutons = {}
        self._soulignements = {}
        self.grid_propagate(False)

        entrees = (
            ("utilisateurs", "👤  Utilisateurs"),
            ("livres", "📖  Livres"),
            ("parametres", "⚙  Paramètres"),
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, minsize=2)
        for index, (cle, texte) in enumerate(entrees):
            colonne = index * 2
            self.grid_columnconfigure(colonne, weight=1)
            bouton = ctk.CTkButton(
                self,
                text=texte,
                height=54,
                corner_radius=0,
                fg_color="transparent",
                hover_color=theme.BOUTON_SURVOL,
                text_color=theme.TEXTE,
                font=theme.police(14),
                command=lambda valeur=cle: self._sur_changement(valeur),
            )
            bouton.grid(row=0, column=colonne, sticky="nsew")
            self._boutons[cle] = bouton

            soulignement = tk.Frame(self, height=2, bg=theme.CARTE)
            soulignement.grid(row=1, column=colonne, sticky="ew")
            self._soulignements[cle] = soulignement

            if index < len(entrees) - 1:
                separateur = ctk.CTkFrame(
                    self,
                    width=1,
                    fg_color=theme.BORDURE,
                    corner_radius=0,
                )
                separateur.grid(
                    row=0,
                    column=colonne + 1,
                    rowspan=2,
                    sticky="ns",
                )

    def activer(self, cle):
        for nom in self._boutons:
            actif = nom == cle
            self._soulignements[nom].configure(
                bg=theme.TEXTE if actif else theme.CARTE
            )


class BookCard(tk.Frame):
    def __init__(
        self,
        master,
        livre,
        sur_emprunter,
        sur_retourner,
        sur_supprimer,
    ):
        super().__init__(
            master,
            bg=theme.CARTE,
            highlightbackground=theme.BORDURE,
            highlightthickness=1,
            bd=0,
        )

        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=3)
        self.grid_columnconfigure(3, weight=3)

        disponible = livre.getAvailability()
        statut = "Disponible" if disponible else f"Emprunté par {livre.getBorrowerId()}"
        colonnes = (
            ("Titre", livre.getTitle(), 0),
            ("Auteur", livre.getAuthor(), 1),
            ("ISBN", livre.getISBN(), 2),
            ("Statut", statut, 3),
        )

        for entete, valeur, colonne in colonnes:
            tk.Label(
                self,
                text=entete,
                bg=theme.CARTE,
                fg=theme.TEXTE_SECONDAIRE,
                font=(theme.FAMILLE, 12),
                anchor="w",
            ).grid(
                row=0,
                column=colonne,
                sticky="ew",
                padx=(16 if colonne == 0 else 8, 8),
                pady=(12, 2),
            )
            tk.Label(
                self,
                text=valeur,
                bg=theme.CARTE,
                fg=theme.TEXTE,
                font=(theme.FAMILLE, 13),
                anchor="w",
                justify="left",
                wraplength=240 if colonne == 0 else 180,
            ).grid(
                row=1,
                column=colonne,
                sticky="ew",
                padx=(16 if colonne == 0 else 8, 8),
                pady=(0, 4),
            )

        tk.Button(
            self,
            text="🗑",
            width=2,
            bd=0,
            relief="flat",
            bg=theme.CARTE,
            activebackground=theme.BOUTON_SURVOL,
            fg=theme.TEXTE,
            font=(theme.FAMILLE, 14),
            cursor="hand2",
            command=lambda: sur_supprimer(livre),
        ).grid(row=0, column=4, rowspan=2, sticky="ne", padx=(4, 10), pady=(8, 0))

        action = sur_emprunter if disponible else sur_retourner
        tk.Button(
            self,
            text="Emprunter" if disponible else "Retourner",
            bd=1,
            relief="solid",
            bg=theme.BOUTON,
            activebackground=theme.BOUTON_SURVOL,
            fg=theme.TEXTE,
            font=(theme.FAMILLE, 12),
            padx=10,
            pady=2,
            cursor="hand2",
            command=lambda: action(livre),
        ).grid(row=2, column=3, sticky="e", padx=(8, 10), pady=(2, 12))


class UserCard(tk.Frame):
    def __init__(self, master, utilisateur):
        super().__init__(
            master,
            bg=theme.CARTE,
            highlightbackground=theme.BORDURE,
            highlightthickness=1,
            bd=0,
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=3)

        livres = utilisateur.getBorrowedBooks()
        isbns = ", ".join(livres) if livres else "N/A"
        colonnes = (
            ("Id", utilisateur.getUserId(), 0),
            ("Nom", utilisateur.getName(), 1),
            ("Livres empruntés", str(utilisateur.getNumberOfBorrowedBooks()), 2),
            ("ISBNs", isbns, 3),
        )

        for entete, valeur, colonne in colonnes:
            tk.Label(
                self,
                text=entete,
                bg=theme.CARTE,
                fg=theme.TEXTE_SECONDAIRE,
                font=(theme.FAMILLE, 12),
                anchor="w",
            ).grid(
                row=0,
                column=colonne,
                sticky="ew",
                padx=(16 if colonne == 0 else 8, 8),
                pady=(12, 2),
            )
            tk.Label(
                self,
                text=valeur,
                bg=theme.CARTE,
                fg=theme.TEXTE,
                font=(theme.FAMILLE, 13),
                anchor="w",
                justify="left",
                wraplength=280 if colonne == 3 else 200,
            ).grid(
                row=1,
                column=colonne,
                sticky="ew",
                padx=(16 if colonne == 0 else 8, 16),
                pady=(0, 12),
            )


class DialogueBase(ctk.CTkToplevel):
    def __init__(self, master, titre, largeur, hauteur):
        super().__init__(master)
        self.resultat = None
        self.title(titre)
        self.geometry(f"{largeur}x{hauteur}")
        self.resizable(False, False)
        self.configure(fg_color=theme.FOND)
        self.transient(master.winfo_toplevel())
        self.grid_columnconfigure(0, weight=1)
        self.after(50, self._finaliser)

    def _finaliser(self):
        if not self.winfo_exists():
            return
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        try:
            self.grab_set()
        except Exception:
            pass

    def _champ(self, parent, libelle):
        ctk.CTkLabel(
            parent,
            text=libelle,
            font=theme.police(12),
            text_color=theme.TEXTE,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(10, 2))
        entree = ctk.CTkEntry(
            parent,
            height=32,
            corner_radius=4,
            border_width=1,
            border_color=theme.BORDURE,
            fg_color=theme.CARTE,
            text_color=theme.TEXTE,
            font=theme.police(13),
        )
        entree.pack(fill="x", padx=20)
        return entree

    def _boutons(self, parent, texte_valider, commande_valider):
        barre = ctk.CTkFrame(parent, fg_color="transparent")
        barre.pack(fill="x", padx=20, pady=(18, 16))
        ctk.CTkButton(
            barre,
            text="Annuler",
            width=100,
            height=32,
            corner_radius=4,
            fg_color=theme.BOUTON,
            hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            border_width=1,
            border_color=theme.BORDURE,
            font=theme.police(12),
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            barre,
            text=texte_valider,
            width=110,
            height=32,
            corner_radius=4,
            fg_color=theme.BOUTON,
            hover_color=theme.BOUTON_SURVOL,
            text_color=theme.TEXTE,
            border_width=1,
            border_color=theme.BORDURE,
            font=theme.police(12),
            command=commande_valider,
        ).pack(side="right")
