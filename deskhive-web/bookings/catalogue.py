"""Stable public request codes; no SQLite IDs and no change to the M1 JSON."""
from spaces.data import LOCATIONS

SPACE_CODES = {
    "lyo-desk": ("lyo", "Lyon Open Desk"),
    "lyo-room": ("lyo", "Lyon Meeting Room"),
    "lil-desk": ("lil", "Lille Open Desk"),
    "lil-room": ("lil", "Lille Meeting Room"),
    "bcn-desk": ("bcn", "Barcelona Open Desk"),
    "bcn-room": ("bcn", "Barcelona Meeting Room"),
}

def request_spaces():
    result = {}
    for code, (location_code, name) in SPACE_CODES.items():
        location = LOCATIONS[location_code]
        space = next(s for s in location["spaces"] if s["name"] == name)
        result[code] = {**space, "city": location["city"]}
    return result
