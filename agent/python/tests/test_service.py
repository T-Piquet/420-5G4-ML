"""Tests sans fenetre du service Python de la bibliotheque."""

import sys
import tempfile
import unittest
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AGENT_DIR / "python"))

from service import LibraryService  # noqa: E402


BOOKS_FIXTURE = (
    "Le Petit Prince|Antoine de Saint-Exupery|978-1|1|\n"
    "1984|George Orwell|978-2|0|U2\n"
)

USERS_FIXTURE = (
    "Alice|U1|\n"
    "Bob|U2|978-2\n"
)


class LibraryServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.data_dir = base / "data"
        self.fixtures_dir = base / "fixtures"
        self.fixtures_dir.mkdir()

        (self.fixtures_dir / "books.txt").write_text(BOOKS_FIXTURE, encoding="utf-8")
        (self.fixtures_dir / "users.txt").write_text(USERS_FIXTURE, encoding="utf-8")

        self.service = LibraryService(
            data_dir=self.data_dir, fixtures_dir=self.fixtures_dir
        )
        self.service.load()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_chargement_et_copie_des_fixtures(self) -> None:
        self.assertTrue((self.data_dir / "books.txt").is_file())
        self.assertTrue((self.data_dir / "users.txt").is_file())
        self.assertEqual(len(self.service.get_books()), 2)
        self.assertEqual(len(self.service.get_users()), 2)

    def test_ajout_et_suppression_livre(self) -> None:
        book = self.service.add_book("Dune", "Frank Herbert", "978-3")
        self.assertEqual(book["isbn"], "978-3")
        self.assertEqual(self.service.find_book("978-3")["title"], "Dune")
        self.assertEqual(len(self.service.get_books()), 3)

        self.assertTrue(self.service.remove_book("978-3"))
        self.assertIsNone(self.service.find_book("978-3"))
        self.assertFalse(self.service.remove_book("978-3"))

    def test_doublon_isbn(self) -> None:
        with self.assertRaises(ValueError):
            self.service.add_book("Autre titre", "Autre auteur", "978-1")
        self.assertEqual(len(self.service.get_books()), 2)

    def test_ajout_utilisateur_et_doublon(self) -> None:
        user = self.service.add_user("Charlie", "U3")
        self.assertEqual(user["user_id"], "U3")
        self.assertEqual(self.service.find_user("U3")["name"], "Charlie")

        with self.assertRaises(ValueError):
            self.service.add_user("Charlie bis", "U3")
        self.assertEqual(len(self.service.get_users()), 3)

    def test_emprunt_et_retour(self) -> None:
        self.assertTrue(self.service.check_out("978-1", "U1"))
        self.assertFalse(self.service.find_book("978-1")["available"])
        self.assertIn("978-1", self.service.find_user("U1")["borrowed_books"])

        self.assertTrue(self.service.return_book("978-1"))
        self.assertTrue(self.service.find_book("978-1")["available"])
        self.assertEqual(self.service.find_user("U1")["borrowed_books"], [])

        self.assertFalse(self.service.check_out("978-1", "U-inconnu"))
        self.assertFalse(self.service.return_book("978-1"))

    def test_sauvegarde_et_rechargement(self) -> None:
        self.service.add_book("Dune", "Frank Herbert", "978-3")
        self.assertTrue(self.service.save())

        rechargement = LibraryService(
            data_dir=self.data_dir, fixtures_dir=self.fixtures_dir
        )
        rechargement.load()

        self.assertEqual(len(rechargement.get_books()), 3)
        self.assertEqual(rechargement.find_book("978-3")["author"], "Frank Herbert")

    def test_statistiques(self) -> None:
        stats = self.service.get_stats()
        self.assertEqual(stats["total_books"], 2)
        self.assertEqual(stats["available_books"], 1)
        self.assertEqual(stats["checked_out_books"], 1)
        self.assertEqual(stats["total_users"], 2)

        self.service.check_out("978-1", "U1")
        stats = self.service.get_stats()
        self.assertEqual(stats["available_books"], 0)
        self.assertEqual(stats["checked_out_books"], 2)


if __name__ == "__main__":
    unittest.main()
