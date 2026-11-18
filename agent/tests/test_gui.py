#!/usr/bin/env python3
"""Tests of the Tkinter application (requires a display).

They build the real window (hidden), drive the same methods the buttons call,
and check the resulting C++ state.  Run with a display:

    DISPLAY=:0 python3 -m unittest agent.tests.test_gui -v
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import tkinter as tk
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT / "python"))

from gui import App  # noqa: E402
from store import ApiError, Store  # noqa: E402

FIXTURE = AGENT / "tests" / "fixtures" / "data"


@unittest.skipUnless(os.environ.get("DISPLAY"), "Tkinter requires a display")
class GuiSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="biblio-gui-"))
        self.data = self.tmp / "data"
        shutil.copytree(FIXTURE, self.data)
        self.store = Store(self.data)
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = App(self.root, self.store)
        self.root.update()

    def tearDown(self) -> None:
        job = getattr(self.app, "_conflict_job", None)
        if job is not None:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self.root.destroy()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_screens_build(self) -> None:
        for route in ("dashboard", "catalogue", "loans", "users"):
            self.app.show(route)
            self.root.update()
        self.app.show("book", "9782253096337")
        self.root.update()
        self.assertEqual(self.app.state["stats"]["total"], 41)
        self.assertEqual(len(self.app.state["conflicts"]), 1)

    def test_add_edit_and_save(self) -> None:
        self.app.show("book", "")
        self.root.update()
        self.app.entry_title.insert(0, "Test GUI")
        self.app.entry_author.insert(0, "Autrice")
        self.app.entry_isbn.insert(0, "978-2-123-45678-9")
        self.app.submit_book()
        self.root.update()
        self.assertEqual(self.app.state["stats"]["total"], 42)
        self.assertTrue(self.app.state["dirty"])

        title = next(b["title"] for b in self.app.state["books"] if b["isbn"] == "9782123456789")
        self.assertEqual(title, "Test GUI")

        # Duplicate ISBN is rejected with a field error.
        self.app.show("book", "")
        self.root.update()
        self.app.entry_title.insert(0, "Doublon")
        self.app.entry_author.insert(0, "X")
        self.app.entry_isbn.insert(0, "9782070612758")
        self.app.submit_book()
        self.root.update()
        self.assertEqual(self.app.add_error["code"], "duplicate_isbn")

        self.app.show("catalogue")
        self.root.update()
        self.app.save()
        self.root.update()
        self.assertFalse(self.app.state["dirty"])
        self.assertIn("Test GUI", (self.data / "books.txt").read_text(encoding="utf-8"))

    def test_loan_and_return(self) -> None:
        self.app.show("loans")
        self.root.update()
        self.app.loan_book = "9782070612758"
        self.app.loan_user = "USR003"
        self.app.check_out()
        self.root.update()
        self.assertEqual(self.app.state["stats"]["checkedOut"], 15)
        book = next(b for b in self.app.state["books"] if b["isbn"] == "9782070612758")
        self.assertEqual(book["borrowerId"], "USR003")

        self.app.return_book("9782070612758")
        self.root.update()
        self.assertEqual(self.app.state["stats"]["checkedOut"], 14)

    def test_user_creation_and_dialogs(self) -> None:
        self.app.show("users")
        self.root.update()
        self.app.new_name.insert(0, "Nouvelle Personne")
        self.app.submit_user()
        self.root.update()
        self.assertEqual(self.app.state["stats"]["users"], 26)

        self.app.dialog_quit()
        self.root.update()
        self.assertIsNotNone(self.app.dialog)
        self.app.close_dialog()

        self.app.dialog_delete("9782253096337")
        self.root.update()
        self.assertIsNotNone(self.app.dialog)
        self.app.close_dialog()

    def test_backup(self) -> None:
        self.app.save()
        self.app.start_backup()
        self.root.update()
        self.assertTrue((self.data / "books.txt.backup").exists())
        self.assertTrue((self.data / "users.txt.backup").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
