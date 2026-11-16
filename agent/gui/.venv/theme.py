"""Palette et styles inspirés de layoutIdea.svg."""

LIGHT = {
    "background": "#BFD7FF",
    "surface": "#E2FDFF",
    "primary": "#5465FF",
    "secondary": "#788BFF",
    "accent": "#9BB1FF",
    "text_on_primary": "#FFFFFF",
    "text": "#1B2559",
    "text_muted": "#5A6785",
    "border": "#A9BCFF",
    "row_alt": "#F4FBFF",
    "success": "#1F7A5C",
    "success_soft": "#D7F4E8",
    "danger": "#A63737",
    "danger_soft": "#FBE4E4",
    "warning": "#8A5A00",
    "warning_soft": "#FFF1CC",
}

DARK = {
    "background": "#0F172A",
    "surface": "#1B2942",
    "primary": "#4F63D2",
    "secondary": "#6F86FF",
    "accent": "#93A7FF",
    "text_on_primary": "#FFFFFF",
    "text": "#EAF0FF",
    "text_muted": "#A8B6D6",
    "border": "#33456B",
    "row_alt": "#16233A",
    "success": "#4ADE80",
    "success_soft": "#12372B",
    "danger": "#FF8A8A",
    "danger_soft": "#3B1A1F",
    "warning": "#F6C453",
    "warning_soft": "#3A2B0B",
}

Color = tuple[str, str]


def _pair(key: str) -> Color:
    return LIGHT[key], DARK[key]


BACKGROUND = _pair("background")
SURFACE = _pair("surface")
PRIMARY = _pair("primary")
SECONDARY = _pair("secondary")
ACCENT = _pair("accent")
TEXT_ON_PRIMARY = _pair("text_on_primary")
TEXT = _pair("text")
TEXT_MUTED = _pair("text_muted")
BORDER = _pair("border")
ROW_ALT = _pair("row_alt")
SUCCESS = _pair("success")
SUCCESS_SOFT = _pair("success_soft")
DANGER = _pair("danger")
DANGER_SOFT = _pair("danger_soft")
WARNING = _pair("warning")
WARNING_SOFT = _pair("warning_soft")

FONT_FAMILY = "DejaVu Sans"
FONT_TITLE = (FONT_FAMILY, 30, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 17)
FONT_HEADING = (FONT_FAMILY, 23, "bold")
FONT_BODY = (FONT_FAMILY, 15)
FONT_BODY_BOLD = (FONT_FAMILY, 15, "bold")
FONT_SMALL = (FONT_FAMILY, 14)
FONT_METRIC = (FONT_FAMILY, 38, "bold")
