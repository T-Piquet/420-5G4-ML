import customtkinter as ctk

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.title("Application de test")
app.geometry("400x200")

label = ctk.CTkLabel(app, text="Bienvenue !")
label.pack(expand=True)

app.mainloop()
