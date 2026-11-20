import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    CARDS = [
        ("total", "Livres au total"),
        ("disponibles", "Livres disponibles"),
        ("empruntes", "Livres empruntés"),
        ("utilisateurs", "Utilisateurs"),
    ]

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Tableau de bord",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        cards.grid_columnconfigure((0, 1), weight=1, uniform="cards")
        cards.grid_rowconfigure((0, 1), weight=1)

        self.value_labels = {}
        for index, (key, title) in enumerate(self.CARDS):
            card = ctk.CTkFrame(cards)
            card.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=5,
                pady=5,
            )
            value = ctk.CTkLabel(
                card, text="0", font=ctk.CTkFont(size=32, weight="bold")
            )
            value.pack(pady=(15, 0))
            ctk.CTkLabel(card, text=title).pack(pady=(0, 15))
            self.value_labels[key] = value

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 15))
        for index, (label, page) in enumerate(
            [
                ("Gérer les livres", "Livres"),
                ("Emprunts", "Emprunts"),
                ("Utilisateurs", "Utilisateurs"),
                ("Données", "Données"),
            ]
        ):
            actions.grid_columnconfigure(index, weight=1)
            ctk.CTkButton(
                actions, text=label, command=lambda p=page: self.app.show_frame(p)
            ).grid(row=0, column=index, sticky="ew", padx=5)

        self.refresh()

    def refresh(self):
        stats = self.app.service.stats
        for key, label in self.value_labels.items():
            label.configure(text=str(stats[key]))
