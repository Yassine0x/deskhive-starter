import sqlite3
import tempfile
import unittest
from dataclasses import is_dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from deskhive_core.booking import BookingConflictError, InvalidBookingError
from deskhive_core.db import DeskHiveDatabase


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = DeskHiveDatabase(":memory:")
        self.addCleanup(self.db.close)
        self.db.create_schema()
        self.db.add_location("LYO", "Lyon")
        self.space_id = self.db.add_space("LYO", "Lyon Desk", "desk", 1, "12.50")
        self.start = datetime(2030, 1, 15, 10)
        self.end = self.start + timedelta(hours=2)

    def book(self, **kwargs):
        values = dict(space_id=self.space_id, member_email="learner@example.test",
                      start=self.start, end=self.end)
        values.update(kwargs)
        return self.db.add_booking(**values)

    def test_create_schema_is_repeatable(self):
        self.db.create_schema()
        self.assertIsNotNone(self.db.get_space(self.space_id))

    def test_foreign_keys_enabled(self):
        self.assertEqual(self.db.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_get_space_maps_dataclass_and_decimal(self):
        space = self.db.get_space(self.space_id)
        self.assertTrue(is_dataclass(space))
        self.assertEqual(space.hourly_rate, Decimal("12.50"))
        self.assertEqual(space.capacity, 1)

    def test_missing_space_returns_none(self):
        self.assertIsNone(self.db.get_space(-1))

    def test_list_spaces_filters_location(self):
        self.db.add_location("BCN", "Barcelona")
        self.db.add_space("BCN", "Other", "desk", 1, "10")
        self.assertEqual([s.id for s in self.db.list_spaces("lyo")], [self.space_id])
        self.assertEqual(self.db.list_spaces("XXX"), [])

    def test_update_rate_persists(self):
        self.assertTrue(self.db.update_hourly_rate(self.space_id, "19.95"))
        self.assertEqual(self.db.get_space(self.space_id).hourly_rate, Decimal("19.95"))
        self.assertFalse(self.db.update_hourly_rate(-1, "20"))

    def test_invalid_rate_does_not_change_row(self):
        with self.assertRaises(ValueError):
            self.db.update_hourly_rate(self.space_id, "-1")
        self.assertEqual(self.db.get_space(self.space_id).hourly_rate, Decimal("12.50"))

    def test_delete_space(self):
        self.assertTrue(self.db.delete_space(self.space_id))
        self.assertIsNone(self.db.get_space(self.space_id))
        self.assertFalse(self.db.delete_space(self.space_id))

    def test_add_booking_maps_datetimes(self):
        booking_id = self.book()
        booking = self.db.list_bookings(self.space_id)[0]
        self.assertEqual((booking.id, booking.start, booking.end), (booking_id, self.start, self.end))
        self.assertEqual(booking.member_email, "learner@example.test")

    def test_conflict_rolls_back_and_connection_remains_usable(self):
        self.book()
        with self.assertRaises(BookingConflictError):
            self.book(start=self.start + timedelta(minutes=30))
        self.assertEqual(len(self.db.list_bookings(self.space_id)), 1)
        self.assertTrue(self.db.update_hourly_rate(self.space_id, "21"))

    def test_back_to_back_is_allowed(self):
        self.book()
        self.book(start=self.end, end=self.end + timedelta(hours=1))
        self.assertEqual(len(self.db.list_bookings(self.space_id)), 2)

    def test_overlap_on_other_space_is_allowed(self):
        other = self.db.add_space("LYO", "Room", "meeting_room", 6, "25")
        self.book()
        self.book(space_id=other)
        self.assertEqual(len(self.db.list_bookings(other)), 1)

    def test_booking_order_is_chronological(self):
        later = self.book(start=self.end, end=self.end + timedelta(hours=1))
        earlier = self.book()
        self.assertEqual([b.id for b in self.db.list_bookings(self.space_id)], [earlier, later])

    def test_cancel_booking_deletes_and_frees_interval(self):
        booking_id = self.book()
        self.assertTrue(self.db.cancel_booking(booking_id))
        self.assertFalse(self.db.cancel_booking(booking_id))
        self.assertEqual(self.db.list_bookings(self.space_id), [])
        self.book()

    def test_booked_space_is_protected(self):
        self.book()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.delete_space(self.space_id)
        self.assertIsNotNone(self.db.get_space(self.space_id))

    def test_invalid_interval_does_not_insert(self):
        with self.assertRaises(InvalidBookingError):
            self.book(end=self.start - timedelta(hours=1))
        self.assertEqual(self.db.list_bookings(self.space_id), [])

    def test_unknown_space_does_not_insert(self):
        with self.assertRaises(ValueError):
            self.book(space_id=-1)

    def test_invalid_email_does_not_insert(self):
        with self.assertRaises(ValueError):
            self.book(member_email="not-an-email")

    def test_foreign_key_blocks_unknown_location(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add_space("XXX", "Unknown", "desk", 1, "10")

    def test_capacity_and_kind_validation(self):
        for capacity in (0, -1, True, 1.5):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                self.db.add_space("LYO", "X", "desk", capacity, "10")
        with self.assertRaises(ValueError):
            self.db.add_space("LYO", "X", "wrong", 1, "10")

    def test_parameterized_query_keeps_sql_as_data(self):
        name = "Room'); DROP TABLE spaces; --"
        sid = self.db.add_space("LYO", name, "desk", 1, "10")
        self.assertEqual(self.db.get_space(sid).name, name)
        self.assertEqual(len(self.db.list_spaces("LYO")), 2)

    def test_disk_persistence_and_explicit_close(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "example.db"
            db = DeskHiveDatabase(target)
            try:
                db.create_schema()
                db.add_location("LIL", "Lille")
                sid = db.add_space("LIL", "Desk", "desk", 1, "8")
            finally:
                db.close()
            reopened = DeskHiveDatabase(target)
            try:
                self.assertEqual(reopened.get_space(sid).name, "Desk")
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
