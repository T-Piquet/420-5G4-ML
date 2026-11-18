#!/usr/bin/env python3
"""Tests of the application state over the pybind11 C++ core.

No HTTP, no display: they exercise the same Store methods the Tkinter
application calls, on a temporary copy of the seed data.

    python3 -m unittest agent.tests.test_store -v
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT / "python"))
sys.path.insert(0, str(AGENT / "build"))

import biblio_core  # noqa: E402  (built C++ module)
from store import ApiError, Store, format_isbn  # noqa: E402

FIXTURE = AGENT / "tests" / "fixtures" / "data"


class StoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="biblio-store-"))
        self.data = self.tmp / "data"
        shutil.copytree(FIXTURE, self.data)
        self.store = Store(self.data)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------- core
    def test_uses_pybind11_core(self) -> None:
        self.assertIsInstance(self.store.library, biblio_core.Library)
        self.assertIsInstance(self.store.files, biblio_core.FileManager)
        book = self.store.library.find_book("9782070612758")
        self.assertIsInstance(book, biblio_core.Book)
        self.assertEqual(book.title, "Le Petit Prince")

    def test_initial_state(self) -> None:
        state = self.store.state()
        self.assertEqual(state["stats"]["total"], 41)
        self.assertEqual(state["stats"]["users"], 25)
        self.assertEqual(state["stats"]["available"], 27)
        self.assertEqual(state["stats"]["checkedOut"], 14)
        self.assertEqual(state["stats"]["usersWithLoans"], 14)
        self.assertEqual(len(state["loans"]), 14)
        self.assertEqual(len(state["conflicts"]), 1)
        self.assertEqual([a["name"] for a in state["authors"]],
                         ["George Sand", "Victor Hugo", "Molière", "Jean Racine", "Émile Zola"])
        self.assertEqual(next(b for b in state["books"]
                              if b["isbn"] == "9782070612758")["isbnFormatted"],
                         "978-2-07-061275-8")
        self.assertFalse(state["dirty"])

    # ---------------------------------------------------------- validation
    def test_add_book_validation(self) -> None:
        with self.assertRaises(ApiError) as ctx:
            self.store.add_book("", "X", "1")
        self.assertEqual(ctx.exception.field, "title")

        with self.assertRaises(ApiError) as ctx:
            self.store.add_book("T", "A", "9782070612758")
        self.assertEqual(ctx.exception.code, "duplicate_isbn")
        self.assertEqual(ctx.exception.extra["existingTitle"], "Le Petit Prince")

        with self.assertRaises(ApiError) as ctx:
            self.store.add_book("T", "A", "12345")
        self.assertEqual(ctx.exception.field, "isbn")

        with self.assertRaises(ApiError) as ctx:
            self.store.add_book("Ti|tre", "A", "9782123456789")
        self.assertEqual(ctx.exception.field, "title")

        state = self.store.add_book("Test API", "Autrice", "978-2-123-45678-9")
        self.assertTrue(state["dirty"])
        self.assertEqual(state["changes"]["addedBooks"], 1)
        self.assertEqual(state["stats"]["total"], 42)

    def test_edit_book(self) -> None:
        state = self.store.update_book("9782070612758", "Le Petit Prince (édité)", "Saint-Exupéry")
        self.assertEqual(state["changes"]["editedBooks"], 1)
        book = next(b for b in state["books"] if b["isbn"] == "9782070612758")
        self.assertEqual(book["title"], "Le Petit Prince (édité)")

        with self.assertRaises(ApiError):
            self.store.update_book("0000000000000", "X", "Y")

    # --------------------------------------------------------------- loans
    def test_loans(self) -> None:
        state = self.store.check_out("9782070612758", "USR003")
        self.assertEqual(state["stats"]["checkedOut"], 15)
        self.assertEqual(state["changes"]["loanOps"], 1)
        book = next(b for b in state["books"] if b["isbn"] == "9782070612758")
        self.assertEqual(book["borrowerId"], "USR003")

        with self.assertRaises(ApiError) as ctx:
            self.store.check_out("9782070612758", "USR004")
        self.assertEqual(ctx.exception.code, "unavailable")

        state = self.store.return_loan("9782070612758")
        self.assertEqual(state["stats"]["checkedOut"], 14)
        self.assertEqual(state["changes"]["loanOps"], 2)

    def test_delete_borrowed(self) -> None:
        with self.assertRaises(ApiError) as ctx:
            self.store.remove_book("9782253096337")
        self.assertEqual(ctx.exception.code, "borrowed")
        self.assertEqual(ctx.exception.extra["borrowerId"], "USR001")

        state = self.store.remove_book("9782253096337", return_first=True)
        self.assertFalse(any(b["isbn"] == "9782253096337" for b in state["books"]))
        self.assertEqual(state["stats"]["usersWithLoans"], 13)

    # ------------------------------------------------------- save / backup
    def test_save_and_backup(self) -> None:
        self.store.add_book("Sauvegardé", "Auteur", "9782123456789")
        state = self.store.save()
        self.assertFalse(state["dirty"])
        text = (self.data / "books.txt").read_text(encoding="utf-8")
        self.assertIn("Sauvegardé", text)
        self.assertIn("Le Petit Prince", text)

        state = self.store.backup("replace")
        self.assertTrue((self.data / "books.txt.backup").exists())
        self.assertTrue((self.data / "users.txt.backup").exists())
        self.assertTrue(state["backupExists"])

        state = self.store.backup("dated")
        self.assertEqual(len(list(self.data.glob("books.txt.backup-*"))), 1)

    # ----------------------------------------------------------- conflicts
    def test_conflicts_and_reconcile(self) -> None:
        conflict = self.store.state()["conflicts"][0]
        self.assertEqual(conflict["kind"], "mismatch")
        self.assertEqual(conflict["userId"], "USR010")
        self.assertEqual(conflict["bookTitle"], "Indiana")
        self.assertEqual(conflict["userTitle"], "Corinne")

        state = self.store.reconcile("USR010", "", "user")
        self.assertEqual(state["conflicts"], [])
        books = {b["title"]: b for b in state["books"]}
        self.assertFalse(books["Corinne"]["available"])
        self.assertEqual(books["Corinne"]["borrowerId"], "USR010")
        self.assertTrue(books["Indiana"]["available"])

    def test_conflict_can_be_ignored(self) -> None:
        state = self.store.reconcile("USR010", "", "ignore")
        self.assertEqual(state["conflicts"], [])
        # A fresh Store over the same files still reports it.
        self.assertEqual(len(Store(self.data).state()["conflicts"]), 1)

    # ------------------------------------------------------------ users
    def test_add_user(self) -> None:
        state = self.store.add_user("Nouvelle Personne")
        self.assertEqual(state["stats"]["users"], 26)
        created = state["users"][-1]
        self.assertEqual(created["id"], "USR026")
        self.assertEqual(created["name"], "Nouvelle Personne")

        with self.assertRaises(ApiError):
            self.store.add_user("")
        with self.assertRaises(ApiError):
            self.store.add_user("Nom|invalide")

    # ------------------------------------------------------------- format
    def test_isbn_formatting(self) -> None:
        self.assertEqual(format_isbn("9782253096337"), "978-2-253-09633-7")
        self.assertEqual(format_isbn("9782070612758"), "978-2-07-061275-8")
        self.assertEqual(format_isbn("123"), "123")


if __name__ == "__main__":
    unittest.main(verbosity=2)
