"""Jetons de design repris de index.html."""
import tkinter.font as tkfont

import customtkinter as ctk

INK = "#172c29"
TEXT = "#3f544b"
MUTED = "#5f706b"
LINE = "#e3e9e5"
BACKGROUND = "#f6f8f6"
SURFACE = "#ffffff"
SURFACE_ALT = "#f4f7f4"
GREEN = "#1d6a55"
GREEN_DARK = "#17553f"
GREEN_PALE = "#e3f2e9"
GREEN_TEXT = "#23704f"
OCHRE = "#bd7736"
OCHRE_PALE = "#fff1e4"
OCHRE_TEXT = "#8f5820"
DANGER = "#a8402c"
DANGER_DARK = "#8b3323"
DISABLED = "#a7b3ad"
SCROLLBAR = "#c9d3cd"
SPINE_COLORS = ("#1d6a55", "#2f8068", "#174f40", "#4a947b", "#25725c")

SIDEBAR_WIDTH = 236
RADIUS = 12
RADIUS_SMALL = 8
PAGE_PADDING = 32

_SERIF_CANDIDATES = ("Georgia", "Noto Serif", "DejaVu Serif", "Times New Roman")
_SANS_CANDIDATES = ("Inter", "Segoe UI", "Helvetica Neue", "Noto Sans", "DejaVu Sans", "Arial")
_ROLES = {
    "display": ("serif", 32, "normal"),
    "heading": ("serif", 19, "normal"),
    "figure": ("serif", 30, "normal"),
    "brand": ("serif", 20, "normal"),
    "body": ("sans", 13, "normal"),
    "strong": ("sans", 13, "bold"),
    "small": ("sans", 12, "normal"),
    "button": ("sans", 13, "bold"),
    "button_small": ("sans", 12, "bold"),
}
_fonts: dict[str, ctk.CTkFont] = {}


def _first_installed(candidates: tuple[str, ...], installed: set[str]) -> str:
    return next((name for name in candidates if name in installed), candidates[-1])


def font(role: str) -> ctk.CTkFont:
    """Retourne la police d'un rôle ; une fenêtre Tk doit déjà exister."""
    if role not in _fonts:
        installed = set(tkfont.families())
        families = {
            "serif": _first_installed(_SERIF_CANDIDATES, installed),
            "sans": _first_installed(_SANS_CANDIDATES, installed),
        }
        family, size, weight = _ROLES[role]
        _fonts[role] = ctk.CTkFont(family=families[family], size=size, weight=weight)
    return _fonts[role]
