import customtkinter as ctk

FOND = "#F6F6F7"
CARTE = "#FFFFFF"
BORDURE = "#9C9C9C"
BORDURE_LEGERE = "#C9C9C9"
TEXTE = "#1A1A1A"
TEXTE_SECONDAIRE = "#5F5F5F"
BOUTON = "#EAEAEA"
BOUTON_SURVOL = "#DBDBDB"
ACTIF = "#D3D3D3"
ERREUR = "#B3261E"
FAMILLE = "DejaVu Sans"


def police(taille, poids="normal"):
    return ctk.CTkFont(family=FAMILLE, size=taille, weight=poids)
