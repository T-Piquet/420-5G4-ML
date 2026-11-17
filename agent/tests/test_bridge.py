"""Integration tests for the pybind11 C++ bridge and BibliothequeAPI."""

import sys
import tempfile
import unittest
from pathlib import Path

GUI_DIR = Path(__file__).resolve().parent.parent / "gui"
if str(GUI_DIR) not in sys.path:
    sys.path.insert(0, str(GUI_DIR))

from bibliotheque_api import BibliothequeAPI  # noqa: E402


class TestBridge(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.api = BibliothequeAPI(data_dir=self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_add_and_remove_book(self) -> None:
        ok, _ = self.api.add_book("Clean Code", "Robert C. Martin", "978-0132350884")
        self.assertTrue(ok)
        self.assertEqual(len(self.api.get_all_books()), 1)

        ok, _ = self.api.add_book("Duplicate", "Author", "978-0132350884")
        self.assertFalse(ok)

        ok, _ = self.api.remove_book("978-0132350884")
        self.assertTrue(ok)
        self.assertEqual(len(self.api.get_all_books()), 0)

    def test_search_and_stats(self) -> None:
        self.api.add_book("1984", "George Orwell", "ISBN-1")
        self.api.add_book("Dune", "Frank Herbert", "ISBN-2")
        self.api.add_user("Alice", "U1")
        self.api.checkout_book("ISBN-1", "U1")

        self.assertIsNotNone(self.api.find_book_by_isbn("ISBN-1"))
        self.assertEqual(len(self.api.search_books_by_title("dun")), 1)
        self.assertEqual(len(self.api.search_books_by_author("orwell")), 1)
        self.assertEqual(len(self.api.get_available_books()), 1)

        stats = self.api.get_stats()
        self.assertEqual(stats["total_books"], 2)
        self.assertEqual(stats["available_books"], 1)
        self.assertEqual(stats["checked_out_books"], 1)
        self.assertEqual(stats["total_users"], 1)

    def test_add_edit_user_and_checkout_return(self) -> None:
        self.assertTrue(self.api.add_book("1984", "George Orwell", "ISBN-1")[0])
        self.assertTrue(self.api.add_user("Alice", "U1")[0])
        self.assertTrue(self.api.update_user_name("U1", "Alice Martin")[0])

        self.assertEqual(self.api.get_all_users()[0].name, "Alice Martin")

        # Checkout succeeds and blocks book deletion
        self.assertTrue(self.api.checkout_book("ISBN-1", "U1")[0])
        self.assertFalse(self.api.remove_book("ISBN-1")[0])

        # Return succeeds and allows book deletion
        self.assertTrue(self.api.return_book("ISBN-1")[0])
        self.assertTrue(self.api.remove_book("ISBN-1")[0])

    def test_save_backup_and_reload(self) -> None:
        self.api.add_book("Dune", "Frank Herbert", "ISBN-2")
        self.api.add_user("Bob", "U2")
        self.assertTrue(self.api.save())
        self.assertTrue(self.api.create_backup()[0])

        reloaded = BibliothequeAPI(data_dir=self.tmp_dir.name)
        self.assertEqual(len(reloaded.get_all_books()), 1)
        self.assertEqual(len(reloaded.get_all_users()), 1)


if __name__ == "__main__":
    unittest.main()
