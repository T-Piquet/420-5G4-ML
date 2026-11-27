import customtkinter as ctk

ctk.set_appearance_mode("System")
app = ctk.CTk()
app.title("Bibliothèque")
app.geometry("500x260")

books = []

title_entry = ctk.CTkEntry(app, placeholder_text="Titre")
title_entry.pack(padx=16, pady=(16, 6), fill="x")

author_entry = ctk.CTkEntry(app, placeholder_text="Auteur")
author_entry.pack(padx=16, pady=6, fill="x")

isbn_entry = ctk.CTkEntry(app, placeholder_text="ISBN")
isbn_entry.pack(padx=16, pady=6, fill="x")

status_label = ctk.CTkLabel(app, text="Total livres : 0")
status_label.pack(padx=16, pady=8)

ctk.CTkButton(app, text="Ajouter un livre", command=add_book).pack(padx=16, pady=(4, 16))

app.mainloop()