# M5 — Models and Dynamic Webpages

This student checkpoint includes the completed M4 exercises. Only the M5 exercises described in M5-EXERCISES.md remain to be completed.

## Run on Windows

From THIS repository root, use Python 3.12 and a separate environment:

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
& ./.venv/Scripts/python.exe -m pip install --no-build-isolation -e ./deskhive-core
& ./.venv/Scripts/python.exe deskhive-web/manage.py migrate
& ./.venv/Scripts/python.exe check.py --m5
& ./.venv/Scripts/python.exe deskhive-web/manage.py runserver
```

On macOS use `python3.12 -m venv .venv` then `./.venv/bin/python`.
Open `/bookings/manage/` for the M5 labs and `/bookings/new/` to save a booking.

## Contract

- Location has an explicit string primary key. Space, Member and Booking have automatic integer primary keys. Space.code and Member.email are unique. TimestampedModel demonstrates abstract inheritance without another database table.
- Django ORM is the live catalogue source. The data migration installs three locations and six spaces once. `spaces/data.py` is historical M1/M2 seed input only; changing it does not change the web catalogue. The old core SQLite prototype remains a separate M2 exercise.
- Fields and initial migrations are supplied so every starter can migrate and browse immediately. Lab 1 focuses on reading/extending this schema and implementing Booking.clean. `makemigrations --check --dry-run` must remain clean after the required tasks.
- Dates use Europe/Paris and aware datetimes. The M4 adapter rejects ambiguous/nonexistent input and intervals crossing an offset change. Duration must be positive and at most 12 hours. Overlaps use half-open intervals: an end equal to another start is allowed.
- All booking writes go through bookings/services.py. `save_booking` obtains a SQLite write lock before validation; it validates again even after an AJAX check. Busy SQLite writes ask the user to retry. This lock strategy is specific to the classroom SQLite backend. Direct ORM save/update bypasses this service and can bypass validation.
- The M4 request/thanks pages remain a nonpersistent form demonstration. The M5 new/edit pages persist real bookings.
- Lists, edits and deletes are limited to booking IDs in the browser session. This is a classroom demo without authentication, email verification or a production account system. Availability never exposes member details. Removing a booking retains the member record.
- GET never deletes. POST uses CSRF. Valid saves redirect; invalid saves redisplay input and errors. Availability is read-only JSON and disables caching. When editing, the existing booking still occupies its interval in the public availability check; saving an unchanged booking excludes itself correctly.
- jQuery 3.7.1 full build is vendored locally, including its license header, from https://code.jquery.com/jquery-3.7.1.min.js. No CDN connection is needed in class.

## Validation

`check.py --m5` covers the web regression and M5 acceptance tests. `--all` also covers the 42 core tests. The starter deliberately fails M5 acceptance until its TODOs are complete; the M4/core prerequisite checks must pass. Read M5-EXERCISES.md for exact tasks. No quiz, slides or LMS publication is included in this code preparation.

Reference APIs: [Django 5.2 model instance validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/) and [official jQuery releases](https://releases.jquery.com/jquery/).
