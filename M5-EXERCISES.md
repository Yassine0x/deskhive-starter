# M5 — DeskHive labs

Work in the M5 branch and read M5-README.md first. M4 has already been completed in this checkpoint; do not redo its three TODOs.

## Lab 1 — Modelling DeskHive Spaces, Members and Bookings

Read `spaces/models.py`, `bookings/models.py` and their migrations. Draw Location → Space → Booking ← Member. Identify the explicit PK, automatic PKs, unique fields, decimal price, ForeignKey relations, PROTECT policy and inherited created_at. Explain why TimestampedModel is abstract and has no table. The schema scaffold and migrations are supplied to keep this starter bootable.

Implement `Booking.clean()` in `deskhive-web/bookings/models.py`. Call `super().clean()`, validate the interval through `local_interval` and the supplied core validator, translate InvalidBookingError into Django ValidationError, then reject an overlapping booking on the same space. Exclude the current PK. Check only when both dates exist; model field validation handles missing values.

For a field/migration practice in a disposable branch, add a defaulted description TextField to Space, generate/apply a migration and inspect it with sqlmigrate. Revert that optional experiment before the required acceptance check.

Acceptance: seed/key/inheritance, invalid interval, price/capacity constraints, unchanged booking update and overlap tests in `bookings/test_m5.py` pass after the CRUD lab is complete. Run `manage.py makemigrations --check --dry-run` to check schema consistency.

## Lab 2 — Managing DeskHive Bookings through the ORM

Complete the three TODO functions in `deskhive-web/bookings/services.py`:

- `is_available`: overlap means existing.start < end AND existing.end > start; exclude the optional booking PK. Return a boolean with exists().
- `save_booking`: inside the supplied atomic transaction, first perform a no-op Space capacity update using F to obtain SQLite's write lock. Get or create a Member using lowercased email and full_name in defaults. Populate a new or existing Booking, call full_clean, save and return it. A rejected booking must roll back a newly created member too.
- `delete_booking`: delete the supplied booking. The HTTP view has already checked session ownership and CSRF.

Use `manage.py shell` to create/get/filter a booking, change an interval through the service, then delete it. Explain why QuerySet.update does not call full_clean and why availability alone cannot reserve a slot.

Acceptance: create/read/update/delete, adjacent and conflicting intervals, rollback, session ownership and CSRF tests pass. No reservation may be created on a conflicting interval.

## Lab 3 — Adding Collapsible Space Details and a Live Availability Check

Complete `availability` in `deskhive-web/bookings/views_m5.py`: preserve form validation and return JSON with the boolean `available` key using the service. Invalid input remains HTTP 400 and the endpoint stays read-only/no-cache.

Complete `deskhive-web/bookings/static/bookings/m5.js` using the supplied jQuery full build. Toggle hidden details by aria-controls and keep aria-expanded and button text in sync. For the check button, send space/start/end to the form's data-availability-url with $.ajax. Show loading, available, conflict, invalid-input and network-error messages in #availability. Use .text(), never interpolate server strings as HTML. Disable the button while loading; restore it after success/error. Invalidate or abort stale requests when values change. Saving must still work with JavaScript disabled.

Acceptance: run `check.py --m5`. Manually verify details with keyboard, a free interval, a conflicting interval, invalid/missing dates, network failure and a changed interval while a request is pending. Two browser sessions cannot edit/delete each other's bookings. With JavaScript disabled, create/edit/delete still work. The HTTP tests verify server contracts and wiring; they do not execute browser JavaScript.
