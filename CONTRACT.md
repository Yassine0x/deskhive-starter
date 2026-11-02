# DeskHive sections 1 and 2 contract

DeskHive is a fictional coworking network in Lyon, Lille and Barcelona. This contract applies to both the learner starter and instructor solution. All names are fixed to let the same tests verify both.

## Section 1 public site

Project folder `deskhive-web`, Django project package `deskhive`, apps `spaces` and `bookings`. The latter has no business implementation yet. Catalogue source: `spaces/data.py`, dictionary `LOCATIONS`, lowercase keys `lyo`, `lil`, `bcn`. Each record has `city`, `address`, `spaces`; each space has `name`, `kind`, `capacity`, `hourly_rate` as a decimal string. Exactly three locations and six spaces.

| URL | Callable | URL name | Result |
|---|---|---|---|
| `/` | `home(request)` | `spaces:home` | 200 HTML introduction and navigation |
| `/locations/` | `location_list(request)` | `spaces:location_list` | 200 HTML links to locations |
| `/locations/<slug:code>/` | `location_detail(request, code)` | `spaces:location_detail` | 200 HTML or 404 for unknown code |
| `/locations/<slug:code>/summary.json` | `location_summary(request, code)` | `spaces:location_summary` | 200 JSON or 404 for unknown code |
| `/about/` | `AboutView.get(self, request)` | `spaces:about` | 200 HTML, class-based View |

GET and HEAD are accepted. At view level POST is rejected with 405. A real POST without a CSRF token is rejected earlier by Django's CSRF middleware with 403; the default test client skips this protection, so the tests explicitly demonstrate both behaviours. `APPEND_SLASH` defaults to True: `/locations` redirects to `/locations/` with 301. The `.json` route has no final slash. `reverse()` builds all internal links. Values inserted into HTML must be escaped; the supplied `page()` helper uses `format_html`. Query parameters do not alter route matching and are currently ignored.

JSON shape: `{"code":"lyo","city":"Lyon","address":"...","spaces":[{"name":"Lyon Open Desk","kind":"desk","capacity":1,"hourly_rate":"12.00"}, ...]}`. Return the actual address and both catalogue spaces, not literal ellipses. This is a JsonResponse exercise, not a REST framework API.

## Section 2 booking functions

- `validate_booking(start: datetime, end: datetime) -> None`: positive duration, at most 12 hours; otherwise `InvalidBookingError`. Inputs must be local naive datetimes. No future-date, opening-hour or attendance rule is imposed yet.
- `overlaps(a_start, a_end, b_start, b_end) -> bool`: validate both intervals; half-open comparison, so adjacent endpoints do not conflict. Identical, partial and contained intervals conflict.
- `compute_price(hourly_rate, start, end) -> Decimal`: validate interval and positive finite rate; ceil duration to next half hour, then round price to cents HALF_UP. Prefer rates as decimal strings, Decimal or integers. Examples: 90 min at 20 -> 30.00; 31 min at 20 -> 20.00; 2.5 h at 12 -> 30.00.
- Invalid rates raise ValueError. Rejected intervals and database conflicts log warnings. `BookingConflictError` is raised by the repository when a valid interval overlaps another booking for the same space.

The standalone `deskhive-lab1/booking.py` is the first debugging checkpoint. After fixing it, move that same implementation into `deskhive_core/booking.py`; do not maintain two different rule sets. Provided standalone tests import `booking`; packaged tests import `deskhive_core.booking` and use its corresponding logging name.

## Section 2 SQLite repository

`DeskHiveDatabase(path="deskhive.db")` owns one connection, exposed as `connection`, with sqlite3.Row and foreign keys ON. `create_schema() -> None` creates the three prescribed tables and is repeatable. Explicitly `close() -> None` when done. A connection's transaction context commits or rolls back but does not close it.

| Method | Return | Important behaviour |
|---|---|---|
| `add_location(code, city)` | None | Normalize 3-letter ASCII code to uppercase; duplicate PK raises sqlite3.IntegrityError |
| `add_space(location_code, name, kind, capacity, hourly_rate)` | int ID | kind desk/meeting_room, integer capacity >=1, positive finite rate; FK required |
| `get_space(space_id)` | Space or None | Missing row is not a crash |
| `list_spaces(location_code)` | list[Space] | Filter by normalized code, ordered by id; missing location -> [] |
| `update_hourly_rate(space_id, hourly_rate)` | bool | True iff a row matched; invalid rate -> ValueError |
| `delete_space(space_id)` | bool | True iff removed; booked space -> sqlite3.IntegrityError; absent -> False |
| `add_booking(space_id, member_email, start, end)` | int ID | Reuse validate_booking and overlaps; unknown space/invalid simple email -> ValueError; conflict -> BookingConflictError |
| `list_bookings(space_id)` | list[Booking] | Ordered by start then id; missing -> [] |
| `cancel_booking(booking_id)` | bool | Physical DELETE; absent -> False; interval becomes available |

Space dataclass fields: `id, location_code, name, kind, capacity, hourly_rate` (Decimal). Booking: `id, space_id, member_email, start, end` (datetime values). No Django inheritance or ORM is involved. SQL rates use TEXT; dataclass mapping converts them to Decimal. SQL timestamps use consistently formatted ISO strings with microseconds, converted back to naive datetime. Email checking only requires a nonempty local part and domain around one @, not a complete email-validation system.

Use `?` parameters for every data value. To prevent two repository calls from both checking a free slot before writing, the instructor uses an explicit `BEGIN IMMEDIATE` inside the connection transaction context. Validation occurs before opening this write transaction; conflicts roll it back. This is a small SQLite teaching solution, not a production booking architecture. Do not call add_booking from inside an already open user transaction.

`bin/seed_db.py` reads the sibling Web catalogue without starting or importing Django. Codes become uppercase in SQL. It creates exactly 3 locations, 6 spaces and 5 one-hour bookings on 2030-01-15. Those are deterministic example data; they remain valid because no future-date rule is required. IDs come from inserts, not fixed assumptions. Existing target files are refused. The Web pages continue to use the in-memory catalogue, not this database, until a later module.
