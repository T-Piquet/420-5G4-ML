"""
View module - customtkinter GUI implementation
"""
import customtkinter as ctk
from typing import Callable, Optional
from constants import COLORS, SIDEBAR_WIDTH, ICONS
from model import LibraryModel


class BaseCTKFrame(ctk.CTkFrame):
    """Base frame with common styling"""
    def __init__(self, master, height: int = None, **kwargs):
        super().__init__(master=master, **kwargs)
        self._set_styles()
        
        if height:
            self.grid_rowconfigure(0, weight=1)
    
    def _set_styles(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure this frame's colors
        self.configure(fg_color=COLORS["card_bg"])


class BaseCTKButton(ctk.CTkButton):
    """Base button with common styling"""
    def __init__(self, *args, height=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if height:
            self.configure(height=height)
            
        # Apply accent color and radius
        self.configure(
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#1a1b26",
            corner_radius=8,
            font=(ctk.get_default_fontfamily(), FONTS["size_base"]),
        )


class BaseCTKLabel(ctk.CTkLabel):
    """Base label with common styling"""
    def __init__(self, master, text: str = "", **kwargs):
        super().__init__(master=master, text=text, font=(ctk.get_default_fontfamily(), FONTS["size_base"]), **kwargs)


class SidebarButton(ctk.CTkFrame):
    """Sidebar button with icon and hover effect"""
    
    def __init__(self, master, command: Callable = None, icon_name: str = "home", title: str = "Dashboard"):
        super().__init__(master=master, width=SIDEBAR_WIDTH, height=60, fg_color="transparent")
        self.command = command
        self.title = title
        self._create_widget()
    
    def _create_widget(self):
        # Create a frame for the icon and text
        main_frame = ctk.CTkFrame(self, width=SIDEBAR_WIDTH - 48, height=60)
        main_frame.pack(side="left", fill="both", expand=True)
        
        # Add padding
        pad_frame = ctk.CTkFrame(main_frame, width=12, height=60, fg_color="transparent")
        pad_frame.pack(side="left", fill="none", expand=False)
        
        # Create button for click area
        btn = ctk.CTkButton(
            main_frame,
            text=self.title,
            command=self.command if self.command else lambda: None,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            font=(ctk.get_default_fontfamily(), FONTS["size_base"]),
            width=SIDEBAR_WIDTH - 64,
            height=60,
        )
        btn.pack(side="left", fill="both", expand=True)
        
        # Add icon as label
        if self.title:  # Not for divider items
            icon_label = ctk.CTkLabel(
                pad_frame,
                text=ICONS.get(icon_name.lower(), "📚"),
                font=("Segoe UI Emoji", ICONS["icon_size"] or 24),
            )
            icon_label.pack(side="left")


class DashboardFrame(BaseCTKFrame):
    """Dashboard section with statistics"""
    
    def __init__(self, model: LibraryModel, master):
        super().__init__(master, height=None)
        self.model = model
        self._create_widgets()
    
    def _update_stats(self):
        """Update dashboard statistics"""
        self.stats_books_label.configure(text=f"📚 {self.model.get_book_count()} livres")
        self.stats_users_label.configure(text=f"👥 {self.model.get_user_count()} adhérents")
        self.stats_borrowing_label.configure(text=f"📖 {self.model.get_active_borrowing_count()} emprunts actuels")
    
    def _create_widgets(self):
        # Title
        title_frame = ctk.CTkFrame(self, height=48)
        title_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], 0))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🏠 Tableau de bord",
            font=(ctk.get_default_fontfamily(), FONTS["size_large"]),
        )
        title_label.pack(side="left")
        
        # Stats grid
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        
        # Create 4 cards in a grid
        self.stats_cards = []
        for i, stat in enumerate(DASHBOARD_STATS):
            card = ctk.CTkFrame(
                stats_frame,
                width=SIDEBAR_WIDTH // 2 - 16,
                height=100,
                corner_radius=8,
            )
            card.grid(row=0 if i < 2 else 1, column=i % 2, padx=4, pady=4)
            
            # Create colored inner frame
            inner = ctk.CTkFrame(card, height=96, fg_color=f"#{stat['color']}", corner_radius=8)
            inner.pack(fill="both", expand=True)
            
            # Content container with transparent bg
            content = ctk.CTkFrame(inner, height=92, width="100%", fg_color="transparent")
            content.pack(fill="both", expand=True, padx=4, pady=4)
            
            # Title and icon
            title_frame = ctk.CTkFrame(content, height=32)
            title_frame.pack(fill="x", expand=False)
            
            icon_label = ctk.CTkLabel(
                title_frame,
                text=stat["icon"],
                font=("Segoe UI Emoji", 24),
            )
            icon_label.pack(side="left")
            
            stat_title_label = ctk.CTkLabel(
                title_frame,
                text=stat["label"],
                font=(ctk.get_default_fontfamily(), FONTS["size_base"]),
            )
            stat_title_label.pack(side="left", padx=8)
            
            # Value (updated dynamically)
            value_frame = ctk.CTkFrame(content, height=56, fg_color="transparent")
            value_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
            
            stat_value_frame = ctk.CTkFrame(value_frame, height=52)
            stat_value_frame.pack(fill="both", expand=True)
            
            # Label for stats - set later
            label = ctk.CTkLabel(
                stat_value_frame,
                text=f"📊 {stat['label']}",  # Placeholder
                font=(ctk.get_default_fontfamily(), FONTS["size_small"]),
            )
            label.pack(side="left")
            
            self.stats_cards.append({
                "frame": content,
                "label": label,
                "color": stat["color"],
            })
        
        # Update initial stats
        for i, stat in enumerate(DASHBOARD_STATS):
            book_count = self.model.get_book_count() if i == 0 else 0
            user_count = self.model.get_user_count() if i == 1 else 0
            borrowing_count = self.model.get_active_borrowing_count() if i == 2 else 0
            
            stat_label = self.stats_cards[i]["label"]
            stat_frame = self.stats_cards[i]["frame"]
            
            stat_label.configure(text=f"{stat['icon']} {book_count} livres" if i == 0 else
                                f"{stat['icon']} {user_count} adhérents" if i == 1 else
                                f"{stat['icon']} {borrowing_count} emprunts actuels")
            stat_frame.configure(fg_color=f"#{stat['color']}")


class SearchFrame(BaseCTKFrame):
    """Search and filter toolbar"""
    
    def __init__(self, model: LibraryModel, master, title: str = "Recherche"):
        super().__init__(master, height=48)
        self.model = model
        
        # Title label
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=(ctk.get_default_fontfamily(), FONTS["size_base"]),
        )
        title_label.pack(side="left")
        
        # Search entry
        self.search_var = ctk.StringVar()
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(side="right", fill="none", expand=True, padx=8)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder=f"Rechercher dans {title.lower()}...",
            variable=self.search_var,
            font=(ctk.get_default_fontfamily(), FONTS["size_base"]),
        )
        self.search_entry.pack(side="right", fill="x", expand=True, padx=4)
        
        # Search button
        search_btn = ctk.CTkButton(
            search_frame,
            text=ICONS["search"],
            command=self._on_search,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"],
        )
        self.search_btn = search_btn  # Store for callback
        self.search_btn.pack(side="right", fill="none", expand=False)
    
    def _on_search(self):
        query = self.search_var.get()
        if callable(self.on_search):
            self.on_search(query)
    
    def set_on_search(self, callback: Callable):
        self.on_search = callback


class BooksTableFrame(BaseCTKFrame):
    """Books list/table view"""
    
    def __init__(self, model: LibraryModel, master):
        super().__init__(master)
        self.model = model
        
        # Title and actions bar
        header_frame = ctk.CTkFrame(self, height=48)
        header_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], 0))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Catalogue des livres",
            font=(ctk.get_default_fontfamily(), FONTS["size_large"]),
        )
        title_label.pack(side="left")
        
        # Add book button
        add_btn = BaseCTKButton(
            header_frame,
            text=ICONS["add"] + " Ajouter un livre",
            command=self._on_add_book,
            width=160,
        )
        add_btn.pack(side="right")
        
        # Search toolbar
        self.search_frame = SearchFrame(model, master, title="Livres")
        self.search_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]), ipadx=4)
        
        # Books list canvas/scrollable frame
        books_canvas_frame = ctk.CTkScrollableFrame(self, label_text="")
        books_canvas_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        
        self.books_list = []
        self._render_books()
    
    def _render_books(self):
        """Render books list in grid"""
        # Clear existing
        for widget in self.books_list:
            widget.destroy()
        self.books_list.clear()
        
        books = self.model.search_books(self.search_frame.search_var.get())
        
        if not books:
            empty_label = ctk.CTkLabel(
                self.books_canvas_frame,
                text="Aucun livre trouvé",
                font=(ctk.get_default_fontfamily(), FONTS["size_base"]),
            )
            empty_label.pack()
            return
        
        # Create book cards in grid
        row = 0
        col = 0
        for i, book in enumerate(books):
            card_frame = ctk.CTkFrame(self.books_canvas_frame)
            card_frame.grid(row=row, column=col, padx=4, pady=4)
            
            # Book info label
            info_label = ctk.CTkLabel(
                card_frame,
                text=f"{book.title}\n\n{book.author} ({book.year})\nISBN: {book.isbn}",
                font=(ctk.get_default_fontfamily(), FONTS["size_small"]),
                justify="left",
            )
            info_label.pack(fill="both", expand=True)
            
            # Action buttons row (if needed)
            btn_frame = ctk.CTkFrame(card_frame, height=36, fg_color="transparent")
            btn_frame.pack(fill="x", expand=False)
            
            borrow_btn = BaseCTKButton(
                btn_frame,
                text=ICONS["borrow"] + " Emprunter",
                command=lambda b=book: self._on_borrow_book(b),
                width=100,
            )
            borrow_btn.pack(side="left")
            
            self.books_list.append(card_frame)
            
            if (col + 1) % 2 == 0:
                col = 0
                row += 1
            else:
                col += 1
    
    def _on_add_book(self):
        """Open dialog to add book"""
        dialog = ctk.CTkDialog(
            self.master,
            title="Ajouter un livre",
            width=400,
        )
        
        # Create form fields
        title_frame = ctk.CTkFrame(dialog.top_level(), height=36)
        title_frame.pack(fill="x", padx=12, pady=8)
        
        title_label = ctk.CTkLabel(title_frame, text="Titre:")
        title_label.pack(side="left")
        
        title_entry = ctk.CTkEntry(
            title_frame,
            placeholder="Ex: Le Prince et le Moine",
            width=260,
        )
        title_entry.pack(side="right", fill="x", expand=True)
        
        isbn_frame = ctk.CTkFrame(dialog.top_level(), height=36)
        isbn_frame.pack(fill="x", padx=12, pady=8)
        
        isbn_label = ctk.CTkLabel(isbn_frame, text="ISBN:")
        isbn_label.pack(side="left")
        
        isbn_entry = ctk.CTkEntry(
            isbn_frame,
            placeholder="978-...",
            width=260,
        )
        isbn_entry.pack(side="right", fill="x", expand=True)
        
        author_frame = ctk.CTkFrame(dialog.top_level(), height=36)
        author_frame.pack(fill="x", padx=12, pady=8)
        
        author_label = ctk.CTkLabel(author_frame, text="Auteur:")
        author_label.pack(side="left")
        
        author_entry = ctk.CTkEntry(
            author_frame,
            placeholder="Ex: Antoine Volodine",
            width=260,
        )
        author_entry.pack(side="right", fill="x", expand=True)
        
        year_frame = ctk.CTkFrame(dialog.top_level(), height=36)
        year_frame.pack(fill="x", padx=12, pady=8)
        
        year_label = ctk.CTkLabel(year_frame, text="Année:")
        year_label.pack(side="left")
        
        year_entry = ctk.CTkEntry(
            year_frame,
            placeholder="Ex: 2024",
            width=260,
        )
        year_entry.pack(side="right", fill="x", expand=True)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog.top_level(), height=36)
        btn_frame.pack(fill="x", padx=12, pady=8)
        
        confirm_btn = BaseCTKButton(
            btn_frame,
            text="Ajouter",
            command=lambda: self._add_book_action(title_entry, isbn_entry, author_entry, year_entry),
        )
        confirm_btn.pack(side="right")
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=dialog.destroy,
            width=80,
            height=36,
        )
        cancel_btn.pack(side="right")
        
        dialog.geometry("420x360")
        dialog.transient(self.master)
        dialog.grab_set()
    
    def _add_book_action(self, title_entry, isbn_entry, author_entry, year_entry):
        """Handle add book submission"""
        title = title_entry.get()
        isbn = isbn_entry.get()
        author = author_entry.get()
        year = year_entry.get()
        
        if title and isbn and author:
            self.model.add_book(title, isbn, author, year)
            
            # Update display
            self._render_books()
            
            ctk.messagebox.showinfo(
                "Succès",
                f"Livre '{title}' ajouté avec succès!",
            )
        
        dialog.destroy()
    
    def _on_borrow_book(self, book: object):
        """Handle borrow action"""
        # TODO: Implement borrow dialog and action


class UsersTableFrame(BaseCTKFrame):
    """Users list/table view"""
    
    def __init__(self, model: LibraryModel, master):
        super().__init__(master)
        self.model = model
        
        # Header
        header_frame = ctk.CTkFrame(self, height=48)
        header_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], 0))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Adhérents",
            font=(ctk.get_default_fontfamily(), FONTS["size_large"]),
        )
        title_label.pack(side="left")
        
        add_btn = BaseCTKButton(
            header_frame,
            text=ICONS["add"] + " Ajouter un adhérent",
            command=self._on_add_user,
            width=160,
        )
        add_btn.pack(side="right")
        
        # Search toolbar
        self.search_frame = SearchFrame(model, master, title="Adhérents")
        self.search_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]), ipadx=4)
        
        # Users list canvas
        users_canvas_frame = ctk.CTkScrollableFrame(self, label_text="")
        users_canvas_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        
        self.users_list = []
        self._render_users()
    
    def _render_users(self):
        """Render users list"""
        for widget in self.users_list:
            widget.destroy()
        self.users_list.clear()
        
        users = self.model.search_users(self.search_frame.search_var.get())
        
        if not users:
            empty_label = ctk.CTkLabel(
                self.users_canvas_frame,
                text="Aucun adhérent trouvé",
            )
            empty_label.pack()
            return
        
        for user in users:
            card = ctk.CTkFrame(self.users_canvas_frame)
            card.pack(fill="both", expand=True, padx=4, pady=4)
            
            info = ctk.CTkLabel(
                card,
                text=f"{user.name}\n{user.email}",
            )
            info.pack(fill="both", expand=True)


class BorrowingsFrame(BaseCTKFrame):
    """Active borrowings view"""
    
    def __init__(self, model: LibraryModel, master):
        super().__init__(master)
        self.model = model
        
        header_frame = ctk.CTkFrame(self, height=48)
        header_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], 0))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📖 Emprunts en cours",
            font=(ctk.get_default_fontfamily(), FONTS["size_large"]),
        )
        title_label.pack(side="left")
        
        # Active borrowings list
        self.borrowings_list = ctk.CTkScrollableFrame(self)
        self.borrowings_list.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        
        self._render_borrowings()
    
    def _render_borrowings(self):
        """Render active borrowings"""
        for widget in __import__("tkinter").winfo_children(self.borrowings_list):
            if isinstance(widget, ctk.CTkFrame) and widget.winfo_type() == "Frame":
                widget.destroy()
        
        borrowings = self.model.get_active_borrowings()
        
        for borrowing in borrowings:
            card = ctk.CTkFrame(self.borrowings_list)
            card.pack(fill="both", expand=True, padx=4, pady=4)
            
            # Book and user info
            book = __import__("tkinter").winfo_toplevel(self).model.books[0]  # Simplified
            user = __import__("tkinter").winfo_toplevel(self).model.users[0]
            
            info_label = ctk.CTkLabel(
                card,
                text=f"📖 {borrowing.book_id} → 👤 {borrowing.user_id}\n\nDepuis: {borrowing.borrow_date}\nRetour: -",
            )
            info_label.pack(fill="both", expand=True)


class DataFrame(BaseCTKFrame):
    """Data management (export/import) view"""
    
    def __init__(self, model: LibraryModel, master):
        super().__init__(master)
        self.model = model
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="💾 Données & Sauvegardes",
            font=(ctk.get_default_fontfamily(), FONTS["size_large"]),
        )
        title_label.pack(pady=SPACING["md"])
        
        # Info label
        info_label = ctk.CTkLabel(
            self,
            text=f"📊 Livres: {self.model.get_book_count()} | 👥 Adhérents: {self.model.get_user_count()}",
            font=(ctk.get_default_fontfamily(), FONTS["size_small"]),
        )
        info_label.pack(pady=4)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], 0))
        
        export_books_btn = BaseCTKButton(
            btn_frame,
            text=f"📥 Export books.txt ({self.model.get_book_count()} livres)",
            command=self._on_export_books,
            width=200,
        )
        export_books_btn.pack(side="left", fill="x", expand=True)
        
        export_users_btn = BaseCTKButton(
            btn_frame,
            text=f"📥 Export users.txt ({self.model.get_user_count()} adhérents)",
            command=self._on_export_users,
            width=200,
        )
        export_users_btn.pack(side="left", fill="x", expand=True)
        
        save_btn = BaseCTKButton(
            btn_frame,
            text=f"💾 Sauvegarder dans {COLORS['text_primary']}{self.model.data_dir}",
            command=self._on_save,
            width=180,
        )
        save_btn.pack(side="left", fill="x", expand=True)
        
        # Display data directory info
        dir_info = ctk.CTkLabel(
            self,
            text=f"📁 Dossier de données: {self.model.data_dir}",
            font=(ctk.get_default_fontfamily(), FONTS["size_small"]),
        )
        dir_info.pack(pady=SPACING["md"])


class LibraryView:
    """Main view class - creates and manages the entire GUI"""
    
    def __init__(self, model: LibraryModel, window_width: int = 1200, window_height: int = 800):
        self.model = model
        self.master = ctk.CTk()
        
        # Set window title and geometry
        self.master.title("Bibliothèque - Interface Démo")
        self.master.geometry(f"{window_width}x{window_height}")
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.master, width=SIDEBAR_WIDTH, fg_color=COLORS["sidebar"])
        
        # Create main content area
        self.main_frame = ctk.CTkFrame(self.master)
        
        # Layout sidebar and main content
        self.sidebar_frame.pack(side="left", fill="none", expand=False)
        self.main_frame.pack(side="left", fill="both", expand=True)
        
        # Create main grid
        main_container = ctk.CTkFrame(self.main_frame, fg_color=COLORS["main_bg"])
        main_container.pack(fill="both", expand=True)
        
        # Top section - dashboard (2 rows high)
        self.dashboard_frame = DashboardFrame(model, main_container)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=SPACING["md"], pady=(SPACING["md"], 0))
        main_container.grid_rowconfigure(0, weight=DASHBOARD_GRID_ROWS)
        
        # Bottom section - dynamic content area (1 row high)
        self.content_frame = ctk.CTkFrame(main_container, fg_color=COLORS["main_bg"])
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=SPACING["md"], pady=(0, SPACING["md"]))
        main_container.grid_rowconfigure(1, weight=1)
        
        # Load initial data (from CSV or demo data)
        books_file = __import__(os).path.join(model.data_dir, "books.csv")
        users_file = __import__(os).path.join(model.data_dir, "users.csv")
        model.load_from_csv(books_file, users_file)
        
        # Load demo data if files don't exist
        self._load_demo_data()
        
        # Setup navigation callbacks
        self._setup_navigation()
    
    def _load_demo_data(self):
        """Load sample demo data"""
        # Demo books
        demo_books = [
            ("Le Prince et le Moine", "978-2-36804-015-0", "Antoine Volodine", "2024"),
            ("L'Envers du miroir", "978-2-7467-4285-3", "Pierre Michon", "2023"),
            ("Les Fruits de la terre", "978-2-7021-1345-9", "Jean Eustache", "1984"),
        ]
        
        for title, isbn, author, year in demo_books:
            self.model.add_book(title, isbn, author, year)
        
        # Demo users
        demo_users = [
            ("Alice Dupont", "alice@example.com"),
            ("Bob Martin", "bob@example.com"),
        ]
        
        for name, email in demo_users:
            self.model.add_user(name, email)
    
    def _setup_navigation(self):
        """Setup sidebar navigation buttons"""
        # Create a function to create sidebar items
        def create_sidebar_item(icon_name, title, callback):
            frame = ctk.CTkFrame(self.sidebar_frame, height=60, fg_color="transparent")
            frame.pack(fill="both", expand=False)
            
            btn = SidebarButton(
                frame,
                command=callback if callable(callback) else lambda: None,
                icon_name=icon_name,
                title=title,
            )
            btn.pack(fill="both", expand=True)
        
        # Create navigation buttons
        create_sidebar_item("home", "Tableau de bord", lambda: self._show_dashboard())
        create_sidebar_item("books", "Catalogue", lambda: self._show_catalogue())
        create_sidebar_item("users", "Adhérents", lambda: self._show_users())
        create_sidebar_item("borrow", "Emprunts", lambda: self._show_borrowings())
        create_sidebar_item("data", "Données/Sauvegardes", lambda: self._show_data())
    
    def _show_dashboard(self):
        """Show dashboard section"""
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_remove()
    
    def _show_catalogue(self):
        """Show catalogue section"""
        books_frame = BooksTableFrame(self.model, self.content_frame)
        books_frame.grid(row=0, column=0, sticky="nsew")
        
        # Set up search callback
        books_frame.search_frame.set_on_search(lambda q: books_frame._render_books())
    
    def _show_users(self):
        """Show users section"""
        users_frame = UsersTableFrame(self.model, self.content_frame)
        users_frame.grid(row=0, column=0, sticky="nsew")
    
    def _show_borrowings(self):
        """Show borrowings section"""
        borrowings_frame = BorrowingsFrame(self.model, self.content_frame)
        borrowings_frame.grid(row=0, column=0, sticky="nsew")
    
    def _show_data(self):
        """Show data management section"""
        data_frame = DataFrame(self.model, self.content_frame)
        data_frame.grid(row=0, column=0, sticky="nsew")
    
    def _on_export_books(self):
        """Export books to books.txt"""
        save_path = __import__(os).path.join(self.model.data_dir, "books.txt")
        self.model.save_to_csv(save_path, None)
        ctk.ctk messagebox.showinfo("Export", f"Livres exportés vers: {save_path}")
    
    def _on_export_users(self):
        """Export users to users.txt"""
        save_path = __import__(os).path.join(self.model.data_dir, "users.txt")
        self.model.save_to_csv(None, save_path)
        ctk.ctk messagebox.showinfo("Export", f"Adhérents exportés vers: {save_path}")
    
    def _on_save(self):
        """Save all data"""
        self.model.save_to_csv(
            __import__(os).path.join(self.model.data_dir, "books.txt"),
            __import__(os).path.join(self.model.data_dir, "users.txt"),
        )
        ctk.ctk messagebox.showinfo("Sauvegarde", f"Données sauvegardées vers: {self.model.data_dir}")


def create_app(model: LibraryModel = None):
    """Factory function to create the application window and view"""
    if model is None:
        model = LibraryModel()
    
    view = LibraryView(model)
    return view.master, view
