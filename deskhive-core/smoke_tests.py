import unittest
from deskhive_core.db import DeskHiveDatabase

class StarterSmokeTests(unittest.TestCase):
    def test_connection_schema_and_read_work(self):
        db = DeskHiveDatabase(":memory:")
        self.addCleanup(db.close)
        db.create_schema()
        db.add_location("LYO", "Lyon")
        sid = db.add_space("LYO", "Desk", "desk", 1, "12")
        self.assertEqual(db.get_space(sid).name, "Desk")
