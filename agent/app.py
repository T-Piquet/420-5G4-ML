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

def add_book():
    t = title_entry.get().strip()
    a = author_entry.get().strip()
    i = isbn_entry.get().strip()
    if t and a and i:
        books.append((t, a, i))
        status_label.configure(text=f"Ajouté ! Total livres : {len(books)}")
        title_entry.delete(0, "end")
        author_entry.delete(0, "end")
        isbn_entry.delete(0, "end")

ctk.CTkButton(app, text="Ajouter un livre", command=add_book).pack(padx=16, pady=(4, 16))

app.mainloop()