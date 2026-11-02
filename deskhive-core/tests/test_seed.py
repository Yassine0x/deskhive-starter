import runpy
import sqlite3
import tempfile
import unittest
from pathlib import Path


class SeedTests(unittest.TestCase):
    def test_seed_matches_single_catalogue_and_refuses_overwrite(self):
        core = Path(__file__).resolve().parents[1]
        seed = runpy.run_path(str(core / "bin/seed_db.py"))["seed"]
        locations = runpy.run_path(str(core.parent / "deskhive-web/spaces/data.py"))["LOCATIONS"]
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "seed.db"
            seed(target)
            connection = sqlite3.connect(target)
            try:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM locations").fetchone()[0], 3)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM spaces").fetchone()[0], 6)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0], 5)
                for code, location in locations.items():
                    actual = connection.execute(
                        "SELECT name,kind,capacity,hourly_rate FROM spaces WHERE location_code=? ORDER BY id",
                        (code.upper(),),
                    ).fetchall()
                    expected = [(s["name"], s["kind"], s["capacity"], s["hourly_rate"])
                                for s in location["spaces"]]
                    self.assertEqual(actual, expected)
            finally:
                connection.close()
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                seed(target)
            self.assertEqual(target.read_bytes(), before)
