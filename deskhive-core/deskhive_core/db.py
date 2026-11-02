"""An explicit sqlite3 repository; this is NOT a Django model layer."""

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .booking import (
    BookingConflictError, overlaps, positive_rate, validate_booking,
)

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS locations (
    code TEXT PRIMARY KEY,
    city TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS spaces (
    id INTEGER PRIMARY KEY,
    location_code TEXT NOT NULL REFERENCES locations(code) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('desk', 'meeting_room')),
    capacity INTEGER NOT NULL CHECK(capacity >= 1),
    hourly_rate TEXT NOT NULL CHECK(CAST(hourly_rate AS REAL) > 0)
);
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    space_id INTEGER NOT NULL REFERENCES spaces(id) ON DELETE RESTRICT,
    member_email TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    CHECK(end > start)
);
"""


@dataclass(frozen=True)
class Space:
    id: int
    location_code: str
    name: str
    kind: str
    capacity: int
    hourly_rate: Decimal


@dataclass(frozen=True)
class Booking:
    id: int
    space_id: int
    member_email: str
    start: datetime
    end: datetime


def nonempty(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value.strip()


class DeskHiveDatabase:
    """Own one connection. A context manager commits/rolls back; close is explicit."""

    def __init__(self, path="deskhive.db"):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def create_schema(self) -> None:
        self.connection.executescript(SCHEMA)

    def close(self) -> None:
        self.connection.close()

    def add_location(self, code: str, city: str) -> None:
        code = nonempty(code, "code").upper()
        if len(code) != 3 or not code.isascii() or not code.isalpha():
            raise ValueError("Location code must contain three ASCII letters")
        with self.connection:
            self.connection.execute(
                "INSERT INTO locations(code, city) VALUES (?, ?)",
                (code, nonempty(city, "city")),
            )

    def add_space(self, location_code: str, name: str, kind: str,
                  capacity: int, hourly_rate) -> int:
        if type(capacity) is not int or capacity < 1:
            raise ValueError("Capacity must be an integer >= 1")
        if kind not in {"desk", "meeting_room"}:
            raise ValueError("kind must be desk or meeting_room")
        rate = positive_rate(hourly_rate)
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO spaces(location_code, name, kind, capacity, hourly_rate) "
                "VALUES (?, ?, ?, ?, ?)",
                (nonempty(location_code, "location_code").upper(),
                 nonempty(name, "name"), kind, capacity, str(rate)),
            )
        return cursor.lastrowid

    @staticmethod
    def _space(row) -> Space:
        return Space(row["id"], row["location_code"], row["name"], row["kind"],
                     row["capacity"], Decimal(row["hourly_rate"]))

    def get_space(self, space_id: int) -> Space | None:
        row = self.connection.execute(
            "SELECT * FROM spaces WHERE id = ?", (space_id,)
        ).fetchone()
        return self._space(row) if row is not None else None

    def list_spaces(self, location_code: str) -> list[Space]:
        rows = self.connection.execute(
            "SELECT * FROM spaces WHERE location_code = ? ORDER BY id",
            (location_code.upper(),),
        ).fetchall()
        return [self._space(row) for row in rows]

    def update_hourly_rate(self, space_id: int, hourly_rate) -> bool:
        # TODO section 2: update_hourly_rate; see the documented contract.
        raise NotImplementedError("Implement update_hourly_rate")

    def delete_space(self, space_id: int) -> bool:
        """Booked spaces are protected by the FK: raises sqlite3.IntegrityError."""
        with self.connection:
            cursor = self.connection.execute("DELETE FROM spaces WHERE id = ?", (space_id,))
        return cursor.rowcount == 1

    @staticmethod
    def _booking(row) -> Booking:
        return Booking(row["id"], row["space_id"], row["member_email"],
                       datetime.fromisoformat(row["start"]), datetime.fromisoformat(row["end"]))

    def add_booking(self, space_id: int, member_email: str,
                    start: datetime, end: datetime) -> int:
        # TODO section 2: add_booking; see the documented contract.
        raise NotImplementedError("Implement add_booking")

    def list_bookings(self, space_id: int) -> list[Booking]:
        rows = self.connection.execute(
            "SELECT * FROM bookings WHERE space_id = ? ORDER BY start, id", (space_id,)
        ).fetchall()
        return [self._booking(row) for row in rows]

    def cancel_booking(self, booking_id: int) -> bool:
        # TODO section 2: cancel_booking; see the documented contract.
        raise NotImplementedError("Implement cancel_booking")
