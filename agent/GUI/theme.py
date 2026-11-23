"""Thème unique de l'application : palette beige/vert et typographie.

Toutes les couleurs et les polices de l'interface viennent de ce module ;
les vues ne doivent pas coder de couleur en dur.
"""

from __future__ import annotations

import tkinter.font as tkfont

import customtkinter as ctk

# Palette beiges et verts muets.
BACKGROUND = "#F4EFE4"
SURFACE = "#EAE3D2"
HOVER = "#DFD6C1"
SAGE = "#6E7F5F"
SAGE_HOVER = "#5B6A4E"
SAGE_SOFT = "#A9B49B"
TERRACOTTA = "#A4705A"
TEXT = "#33352C"
TEXT_MUTED = "#6C6E62"

CORNER_RADIUS = 6
PAGE_PADDING = 24
CARD_GAP = 6

FONT_CANDIDATES = ("Garamond", "EB Garamond", "DejaVu Serif")

_font_family: str | None = None


def init(root: ctk.CTk) -> None:
    """Résout la famille de police disponible, une fois la fenêtre créée."""
    global _font_family
    available = set(tkfont.families(root))
    _font_family = next(
        (family for family in FONT_CANDIDATES if family in available),
        tkfont.nametofont("TkDefaultFont").actual("family"),
    )


def font(size: int, weight: str = "normal") -> ctk.CTkFont:
    """Retourne une police du thème, dans la famille résolue."""
    if _font_family is None:
        raise RuntimeError("theme.init() doit être appelé avant theme.font().")
    return ctk.CTkFont(family=_font_family, size=size, weight=weight)
