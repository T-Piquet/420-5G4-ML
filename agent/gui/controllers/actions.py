"""Opérations de la bibliothèque, déclenchables depuis n'importe quelle page."""
from gui.models.library_model import LibraryError, LibraryModel
from gui.views.dialogs import ChoiceField, ConfirmDialog, DialogButton, FormDialog, TextField
from gui.views.main_window import MainWindow


class ActionsController:
    def __init__(self, model: LibraryModel, window: MainWindow) -> None:
        self._model = model
        self._window = window

    def add_book(self) -> None:
        def submit(values: dict[str, str], dialog: FormDialog) -> None:
            self._run(dialog, lambda: self._model.add_book(**values),
                      f"Livre ajouté : {values['title']}")

        FormDialog(
            self._window, "Ajouter un livre", "Le livre sera disponible dès son ajout.",
            "Ajouter le livre",
            [
                TextField("title", "Titre", "Le Comte de Monte-Cristo"),
                TextField("author", "Auteur", "Alexandre Dumas"),
                TextField("isbn", "ISBN", "9782070405176"),
            ],
            submit,
        )

    def add_member(self) -> None:
        def submit(values: dict[str, str], dialog: FormDialog) -> None:
            self._run(dialog, lambda: self._model.add_member(**values),
                      f"Utilisateur ajouté : {values['name']}")

        FormDialog(
            self._window, "Ajouter un utilisateur", "L'identifiant doit être unique.",
            "Ajouter l'utilisateur",
            [
                TextField("name", "Nom complet", "Camille Tremblay"),
                TextField("user_id", "Identifiant", "USR026"),
            ],
            submit,
        )

    def lend(self, isbn: str = "", user_id: str = "") -> None:
        books = self._model.available_books()
        members = self._model.members()
        if not books:
            self._window.toast("Aucun livre disponible. Retournez d'abord un livre.", True)
            return
        if not members:
            self._window.toast("Aucun utilisateur inscrit. Ajoutez d'abord un utilisateur.", True)
            return

        def submit(values: dict[str, str], dialog: FormDialog) -> None:
            title = self._model.find_book(values["isbn"]).title
            name = self._model.find_member(values["user_id"]).name
            self._run(dialog, lambda: self._model.check_out(values["isbn"], values["user_id"]),
                      f"{title} : emprunté par {name}")

        FormDialog(
            self._window, "Emprunter un livre", "Choisissez un livre disponible et la personne qui l'emprunte.",
            "Emprunter le livre",
            [
                ChoiceField("isbn", "Livre",
                            [(book.isbn, f"{book.title} ({book.isbn})") for book in books],
                            isbn, "Sélectionner un livre"),
                ChoiceField("user_id", "Utilisateur",
                            [(m.user_id, f"{m.name} ({m.user_id})") for m in members],
                            user_id, "Sélectionner un utilisateur"),
            ],
            submit,
        )

    def return_book(self, isbn: str = "") -> None:
        loans = self._model.loaned_books()
        if not loans:
            self._window.toast("Aucun livre n'est emprunté en ce moment.", True)
            return

        def submit(values: dict[str, str], dialog: FormDialog) -> None:
            title = self._model.find_book(values["isbn"]).title
            self._run(dialog, lambda: self._model.return_book(values["isbn"]),
                      f"Livre retourné : {title}")

        FormDialog(
            self._window, "Retourner un livre", "Le livre redeviendra disponible.",
            "Retourner le livre",
            [ChoiceField("isbn", "Livre emprunté",
                         [(book.isbn, f"{book.title} ({book.isbn})") for book in loans],
                         isbn, "Sélectionner un livre")],
            submit,
        )

    def remove_book(self, isbn: str, title: str) -> None:
        ConfirmDialog(
            self._window, "Supprimer ce livre ?",
            f"« {title} » sera retiré du catalogue.",
            [
                DialogButton("Annuler"),
                DialogButton("Supprimer le livre", lambda: self._remove_book(isbn), "danger"),
            ],
        )

    def save(self) -> bool:
        try:
            self._model.save()
        except LibraryError as error:
            self._window.toast(str(error), is_error=True)
            return False
        self._window.toast("Données enregistrées.")
        return True

    def create_backup(self) -> None:
        try:
            self._model.create_backup()
        except LibraryError as error:
            self._window.toast(str(error), is_error=True)
            return
        if self._model.has_unsaved_changes:
            self._window.toast("Copie créée, sans vos modifications non enregistrées.")
        else:
            self._window.toast("Copie de secours créée.")

    def reload(self) -> None:
        if not self._model.has_unsaved_changes:
            self._reload()
            return
        ConfirmDialog(
            self._window, "Annuler vos modifications ?",
            "Vous reviendrez au dernier enregistrement. Ces modifications seront perdues.",
            [
                DialogButton("Garder mes modifications"),
                DialogButton("Annuler mes modifications", self._reload, "danger"),
            ],
        )

    def _reload(self) -> None:
        self._model.reload()
        self._window.toast("Modifications annulées.")

    def _remove_book(self, isbn: str) -> None:
        try:
            self._model.remove_book(isbn)
        except LibraryError as error:
            self._window.toast(str(error), is_error=True)
            return
        self._window.toast("Livre supprimé.")

    def _run(self, dialog: FormDialog, operation, success_message: str) -> None:
        try:
            operation()
        except LibraryError as error:
            dialog.show_error(str(error))
            return
        dialog.close()
        self._window.toast(success_message)
