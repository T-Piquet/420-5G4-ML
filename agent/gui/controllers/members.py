"""Contrôleur des utilisateurs."""
from functools import partial

from gui.controllers.actions import ActionsController
from gui.controllers.presenters import plural
from gui.models.entities import Member
from gui.models.library_model import LibraryModel
from gui.views.pages.members import MembersPage
from gui.views.table import Action


class MembersController:
    def __init__(self, model: LibraryModel, view: MembersPage, actions: ActionsController) -> None:
        self._model = model
        self._view = view
        self._actions = actions
        view.on_add_member = actions.add_member
        view.on_search = self.refresh

    def refresh(self) -> None:
        query = self._view.search_bar.query
        if query:
            member = self._model.find_member(query)
            members = [member] if member else []
            empty_text = (
                f"Aucun utilisateur n'a l'identifiant {query}.\n"
                "Saisissez-le en entier, avec ses majuscules (USR001)."
            )
        else:
            members = self._model.members()
            empty_text = "Aucun utilisateur inscrit. Ajoutez un premier utilisateur."
        self._view.show_members(
            [self._row(member) for member in members],
            empty_text,
            plural(len(members), "utilisateur"),
        )

    def _row(self, member: Member) -> tuple:
        borrowed = len(member.borrowed_isbns)
        return (
            member.name,
            member.user_id,
            plural(borrowed, "livre") if borrowed else "Aucun",
            (Action("Emprunter un livre", partial(self._actions.lend, "", member.user_id)),),
        )
