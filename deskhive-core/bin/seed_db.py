"""Seed a NEW database from the single web catalogue, without importing Django."""
import argparse
import runpy
from datetime import datetime, timedelta
from pathlib import Path
from deskhive_core.db import DeskHiveDatabase

CORE_ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = CORE_ROOT.parent / "deskhive-web" / "spaces" / "data.py"


def seed(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb"):
        pass
    db = DeskHiveDatabase(target)
    try:
        db.create_schema()
        locations = runpy.run_path(str(CATALOGUE))["LOCATIONS"]
        ids = []
        for code, location in locations.items():
            db.add_location(code.upper(), location["city"])
            for space in location["spaces"]:
                ids.append(db.add_space(code.upper(), **space))
        start = datetime(2030, 1, 15, 10)
        for index in range(5):
            db.add_booking(ids[index], f"member{index+1}@example.test", start, start + timedelta(hours=1))
        counts = [db.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                  for table in ("locations", "spaces", "bookings")]
        print(f"Seeded {target}: locations={counts[0]}, spaces={counts[1]}, bookings={counts[2]}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=CORE_ROOT / "deskhive.db")
    args = parser.parse_args()
    try:
        seed(args.database.resolve())
    except FileExistsError:
        parser.exit(2, "Database already exists. Choose a NEW --database path; no data were changed.\n")
