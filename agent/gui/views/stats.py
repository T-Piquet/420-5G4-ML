import customtkinter as ctk


class StatsView(ctk.CTkFrame):
    ROWS = [
        ("total", "Total des livres"),
        ("disponibles", "Livres disponibles"),
        ("empruntes", "Livres empruntés"),
        ("utilisateurs", "Utilisateurs enregistrés"),
    ]

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Statistiques",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        self.value_labels = {}
        for index, (key, title) in enumerate(self.ROWS, start=1):
            ctk.CTkLabel(self, text=title, anchor="w").grid(
                row=index, column=0, sticky="w", padx=15, pady=8
            )
            value = ctk.CTkLabel(
                self, text="0", font=ctk.CTkFont(size=18, weight="bold")
            )
            value.grid(row=index, column=1, sticky="e", padx=15, pady=8)
            self.value_labels[key] = value

        self.occupancy_label = ctk.CTkLabel(self, text="", anchor="w")
        self.occupancy_label.grid(
            row=len(self.ROWS) + 1, column=0, columnspan=2, sticky="w", padx=15, pady=15
        )

        self.refresh()

    def refresh(self):
        stats = self.app.service.stats
        for key, label in self.value_labels.items():
            label.configure(text=str(stats[key]))

        total = stats["total"]
        taux = (stats["empruntes"] / total * 100) if total else 0
        self.occupancy_label.configure(
            text=f"Taux d'emprunt : {taux:.1f} % ({stats['empruntes']}/{total})"
        )
