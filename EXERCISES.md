# DeskHive learner starter

DeskHive is a fictional coworking company in Lyon, Lille and Barcelona. You will first build its public Django pages, then debug its hourly booking rules, inspect their package and practise SQLite CRUD. This is the order of the first two sections in your LMS.

This is a deliberately incomplete starter, not the final application. The home page runs immediately. Four unfinished public views return **501**, making missing work visible without crashing the server. Section 2 contains exactly the three booking bugs described in your original lab, plus three clearly marked repository TODO methods. See CONTRACT.md for every required behaviour and WINDOWS.md for PowerShell commands.

## Install and prove the starter runs

From this folder, containing requirements.txt and the deskhive-web and deskhive-core directories:

~~~powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
~~~

Do not activate the venv or change PowerShell execution policy. Installation of the separate core package can wait until section 2. Check the Web starter:

~~~powershell
Push-Location .\deskhive-web
& ..\.venv\Scripts\python.exe manage.py check
& ..\.venv\Scripts\python.exe manage.py migrate
& ..\.venv\Scripts\python.exe manage.py test spaces.smoke_tests -v 2
& ..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
~~~

Expected: no system-check issues, two smoke tests pass and http://127.0.0.1:8000/ shows DeskHive. Other public pages currently return 501. Stop the server with Ctrl+C, then `Pop-Location`.

## Section 1 Introduction to Django Web Framework

### A Installation and project layout

Inspect manage.py, deskhive/settings.py, deskhive/urls.py and the apps spaces and bookings. Locate INSTALLED_APPS, TIME_ZONE, DEBUG, ALLOWED_HOSTS, DATABASES and MIDDLEWARE. Follow a GET request through URLconf, view and response. The app bookings has no feature implementation yet.

For the original installation exercise, follow the NEW-directory reconstruction steps in WINDOWS.md. Do not run startproject over this starter. Observe the generated welcome page before wiring public URLs. Return to this supplied pack if you need a known initial state.

### B Public pages

Open spaces/data.py and CONTRACT.md. The dataset and home page are supplied; do not invent a second catalogue. Read the root include and spaces/urls.py. They are wired so the starter runs. Explain how each route name and slug argument works; reproduce that wiring in your installation exercise if you created a fresh skeleton.

Complete these functions in spaces/views.py:

1. location_list(request): list all locations, linking with reverse to their detail pages.
2. location_detail(request, code): display city, address and space details; raise Http404 for unknown code.
3. location_summary(request, code): return exactly the JSON contract; unknown code is 404.
4. AboutView.get(self, request): return an About page using the provided page helper.

Use HttpResponse/JsonResponse directly; no template, model, form or REST framework. Use the supplied page helper and format_html/format_html_join to escape inserted text. All internal links use reverse. Keep the given callable signatures, route names and read-only methods.

From deskhive-web, run the acceptance tests:

~~~powershell
& ..\.venv\Scripts\python.exe manage.py test spaces -v 2
~~~

These 14 tests initially fail because features are missing. After your work, all pass. `spaces.smoke_tests` is a separate one-time preflight for the untouched starter: its 501 expectations cease to apply after completion, so do not use it as a final acceptance suite. It is not included in normal test discovery.

Use curl.exe and browser Network tools as shown in WINDOWS.md. Check 200, 404, 405, a trailing-slash redirect and the JSON response. Record one request path, method, status and Content-Type. Commit your completed pages.

## Section 2 Debugging, Databases and Project Skeletons

### C Fix the existing booking rules once

Edit `deskhive-core/deskhive_core/booking.py` in place. Tests are in `deskhive-core/tests/test_booking.py`. Read CONTRACT.md before fixing code. There are exactly three planted rule defects:

1. Adjacent reservations are incorrectly considered conflicts.
2. Pricing truncates to whole hours instead of rounding up to half hours.
3. Duration validation was disabled, so invalid intervals are accepted.

Run that booking file, inspect it with pdb or your IDE, and use `check.py --rules` from the repository root to run its tests. The acceptance tests provide normal, boundary and exception cases. Add a small reproduction or regression test of your own for each defect before changing the implementation. Follow red, green, refactor; do not change expected values to accommodate a bug. Retain warning logging for rejected intervals. See WINDOWS.md for the commands and pdb controls.

Expected after correction: 19 supplied booking rules tests pass; your extra tests should pass too. An invalid interval raises InvalidBookingError and a back-to-back pair does not conflict. No Django server is needed.

### D Understand and verify the existing package

The skeleton is already supplied. Inspect these exact files without moving or duplicating booking.py:

- `deskhive-core/pyproject.toml`: project name/version, Python requirement and setuptools backend.
- `deskhive-core/deskhive_core/__init__.py`: version 0.1.0.
- `deskhive-core/deskhive_core/booking.py`: the rules you have just fixed.
- `deskhive-core/tests/test_booking.py`: tests importing that same module.
- `deskhive-core/bin/price_quote.py`: a consumer of the installed package.
- `deskhive-core/docs/README.md`: skeleton notes.

Explain the role of each directory and the difference between distribution name deskhive-core and import name deskhive_core. From the repository root:

~~~powershell
& .\.venv\Scripts\python.exe -m pip install --no-build-isolation -e .\deskhive-core
& .\.venv\Scripts\python.exe -c "import deskhive_core; print(deskhive_core.__version__)"
& .\.venv\Scripts\python.exe check.py --rules
& .\.venv\Scripts\python.exe .\deskhive-core\bin\price_quote.py
~~~

macOS equivalents, from the repository root:

~~~bash
./.venv/bin/python -m pip install --no-build-isolation -e ./deskhive-core
./.venv/bin/python -c "import deskhive_core; print(deskhive_core.__version__)"
./.venv/bin/python check.py --rules
./.venv/bin/python deskhive-core/bin/price_quote.py
~~~

Expected: version 0.1.0, all 19 rule tests green, quote EUR 30.00. The same corrected file is reused by SQLite. Commit this milestone; do not repair another copy of the rules.

### E Complete SQLite operations

Edit `deskhive-core/deskhive_core/db.py`. Read its schema, Space/Booking dataclasses and supplied methods. This file already creates and reads a real SQLite database. Finish only its three marked methods:

1. update_hourly_rate: validate the rate, run a parameterized UPDATE in a transaction and return whether a row matched.
2. add_booking: validate the interval/email/space, check existing bookings with overlaps, raise BookingConflictError on a conflict, otherwise insert and return the generated ID. Commit or roll back coherently; see the transaction contract.
3. cancel_booking: delete by ID and return whether a row existed. Cancellation physically removes the row in this prototype.

Never concatenate input into SQL. Preserve the supplied connection's row_factory and foreign-key setting. Close the repository explicitly when finished. Explain why a connection transaction context does not close it.

~~~powershell
Push-Location .\deskhive-core
& ..\.venv\Scripts\python.exe -m unittest -v smoke_tests
& ..\.venv\Scripts\python.exe -m unittest -v tests.test_db
& ..\.venv\Scripts\python.exe -m unittest discover -s tests -v
& ..\.venv\Scripts\python.exe bin/seed_db.py
Pop-Location
~~~

The one core smoke test verifies setup and supplied create/read behaviour; it passes even before TODOs are completed. The DB suite and seed are expected to fail until your methods are implemented. Once complete, all 42 packaged tests pass, and seed creates 3 locations, 6 spaces and 5 bookings. It reads the original spaces/data.py catalogue; keep deskhive-web beside deskhive-core. The Web does not start querying this SQLite prototype yet.

Use a new --database path if a previous seed file exists. See WINDOWS.md for inspecting rows without installing the optional sqlite3 command-line shell.

## Submit

Submit Web views/routes, the corrected rules in deskhive-core/deskhive_core/booking.py, installed package source, tests you added, repository methods and a README of commands and debugging observations. Include a screenshot of a Web success/404 and captured passing test summaries. Include meaningful local Git commits if required by your trainer. Exclude .venv, caches, egg-info and database files; the seed is how another person reproduces the data.

The final check is the 14 Web tests and 42 package tests. The 19 booking rules tests are a subset of the 42 core tests, not another implementation. Do not implement templates, forms, Django business models, DRF, AJAX or XML here.
