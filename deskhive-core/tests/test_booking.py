import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from deskhive_core.booking import (
    InvalidBookingError, compute_price, overlaps, validate_booking,
)


class BookingRulesTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2030, 1, 15, 10)

    def test_hour_price(self):
        self.assertEqual(compute_price("20", self.start, self.start + timedelta(hours=1)), Decimal("20.00"))

    def test_ninety_minutes_price(self):
        self.assertEqual(compute_price("20", self.start, self.start + timedelta(minutes=90)), Decimal("30.00"))

    def test_round_up_to_half_hour(self):
        self.assertEqual(compute_price("20", self.start, self.start + timedelta(minutes=31)), Decimal("20.00"))

    def test_exact_half_hour(self):
        self.assertEqual(compute_price("20", self.start, self.start + timedelta(minutes=30)), Decimal("10.00"))

    def test_microsecond_after_boundary(self):
        self.assertEqual(compute_price("20", self.start, self.start + timedelta(minutes=30, microseconds=1)), Decimal("20.00"))

    def test_cent_rounding(self):
        self.assertEqual(compute_price("0.05", self.start, self.start + timedelta(minutes=30)), Decimal("0.03"))

    def test_zero_duration_rejected(self):
        with self.assertRaises(InvalidBookingError):
            validate_booking(self.start, self.start)

    def test_end_before_start_rejected(self):
        with self.assertRaises(InvalidBookingError):
            validate_booking(self.start, self.start - timedelta(hours=1))

    def test_more_than_twelve_hours_rejected(self):
        with self.assertRaises(InvalidBookingError):
            validate_booking(self.start, self.start + timedelta(hours=12, microseconds=1))

    def test_exactly_twelve_hours_allowed(self):
        self.assertIsNone(validate_booking(self.start, self.start + timedelta(hours=12)))

    def test_aware_datetime_rejected(self):
        aware = self.start.replace(tzinfo=timezone.utc)
        with self.assertRaises(InvalidBookingError):
            validate_booking(aware, aware + timedelta(hours=1))

    def test_invalid_datetime_type_rejected(self):
        with self.assertRaises(InvalidBookingError):
            validate_booking("10:00", "11:00")

    def test_rates_must_be_finite_positive(self):
        for rate in ("0", "-1", "NaN", "Infinity", "wrong", True):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                compute_price(rate, self.start, self.start + timedelta(hours=1))

    def test_adjacent_intervals_do_not_overlap(self):
        a_end = self.start + timedelta(hours=2)
        self.assertFalse(overlaps(self.start, a_end, a_end, a_end + timedelta(hours=2)))

    def test_containment_overlaps(self):
        self.assertTrue(overlaps(self.start, self.start + timedelta(hours=4),
                                 self.start + timedelta(hours=1), self.start + timedelta(hours=2)))

    def test_partial_overlap_is_symmetric(self):
        a_end = self.start + timedelta(hours=2)
        b_start, b_end = self.start + timedelta(hours=1), self.start + timedelta(hours=3)
        self.assertTrue(overlaps(self.start, a_end, b_start, b_end))
        self.assertTrue(overlaps(b_start, b_end, self.start, a_end))

    def test_separate_intervals_do_not_overlap(self):
        self.assertFalse(overlaps(self.start, self.start + timedelta(hours=1),
                                  self.start + timedelta(hours=2), self.start + timedelta(hours=3)))

    def test_identical_intervals_overlap(self):
        end = self.start + timedelta(hours=1)
        self.assertTrue(overlaps(self.start, end, self.start, end))

    def test_rejection_is_logged(self):
        with self.assertLogs("deskhive_core.booking", level="WARNING"):
            with self.assertRaises(InvalidBookingError):
                validate_booking(self.start, self.start - timedelta(minutes=1))


if __name__ == "__main__":
    unittest.main()
