try:
    from .app import main
except ModuleNotFoundError as erreur:
    if erreur.name == "customtkinter":
        raise SystemExit(
            "CustomTkinter est introuvable.\n"
            "Installez les dépendances avec :\n"
            "  .venv/bin/pip install -r requirements.txt"
        ) from erreur
    raise

if __name__ == "__main__":
    main()
