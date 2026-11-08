"""
Constants file - Design system extracted from index.html CSS
"""

# Colors (extracted from CSS variables)
COLORS = {
    "sidebar": "#1a1b26",           # Dark blue-gray sidebar background
    "sidebar_hover": "#24283b",     # Lighter on hover
    "main_bg": "#1f2533",           # Main content background
    "card_bg": "#252e3f",           # Card/panel background
    "text_primary": "#a9b1d6",      # Primary text color
    "text_secondary": "#565f89",   # Secondary/muted text
    "accent": "#7aa2f7",            # Accent/blue accent color
    "accent_hover": "#5d87e4",      # Accent on hover
    "success": "#9ece6a",           # Green for success/actions
    "error": "#f07178",             # Red for errors
    "border": "#3b4252",            # Border color
    "table_header": "#2e3747",      # Table header background
}

# Typography
FONTS = {
    "primary": "Inter, ui-sans-serif, system-ui, sans-serif",
    "size_base": 14,
    "size_small": 12,
    "size_large": 16,
}

# Spacing
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# Sidebar dimensions
SIDEBAR_WIDTH = 200
SIDEBAR_ICON_SIZE = 24

# Dashboard widget stats
DASHBOARD_STATS = [
    {"label": "Livres", "icon": "📚", "color": "#7aa2f7"},
    {"label": "Adhérents", "icon": "👥", "color": "#9ece6a"},
    {"label": "Emprunts actuels", "icon": "📖", "color": "#e0af68"},
]

# Unicode icons (no external icon library)
ICONS = {
    "home": "🏠",      # Dashboard
    "books": "📚",     # Catalogue
    "users": "👥",     # Adhérents
    "borrow": "📖",    # Emprunts
    "data": "💾",      # Données/Sauvegardes
    "add": "➕",       # Add action
    "edit": "✏️",      # Edit action
    "delete": "🗑",    # Delete action
    "search": "🔍",    # Search
    "filter": "🔹",    # Filter
    "export": "📥",    # Export
    "import": "📤",    # Import
}

# Dashboard grid layout
DASHBOARD_GRID_ROWS = 2
DASHBOARD_GRID_COLS = 4
