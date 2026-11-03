# Windows PowerShell commands

Run commands from this pack's root, the folder containing deskhive-web, deskhive-core and deskhive-lab1. Extract the complete pack first. Python 3.12 must already be installed. No virtual environment activation or PowerShell execution-policy change is needed.

## Install once

~~~powershell
py -0p
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& .\.venv\Scripts\python.exe -m pip install --no-build-isolation -e .\deskhive-core
& .\.venv\Scripts\python.exe -c "import deskhive_core; print(deskhive_core.__version__)"
~~~

Expected package version: 0.1.0. setuptools is in requirements.txt; --no-build-isolation reuses that build backend. This is still an editable installation. Use this project's own virtual environment for every command.

## Section 1

~~~powershell
Push-Location .\deskhive-web
& ..\.venv\Scripts\python.exe -m django --version
& ..\.venv\Scripts\python.exe manage.py check
& ..\.venv\Scripts\python.exe manage.py migrate
& ..\.venv\Scripts\python.exe manage.py test spaces -v 2
& ..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
~~~

The server blocks this terminal. Open http://127.0.0.1:8000/ in a browser. Use another terminal for these checks (they do not depend on its working directory):

~~~powershell
curl.exe -I http://127.0.0.1:8000/
curl.exe -i http://127.0.0.1:8000/locations/lyo/
curl.exe -i http://127.0.0.1:8000/locations/xyz/
curl.exe http://127.0.0.1:8000/locations/lyo/summary.json
~~~

Expected: HEAD 200; known location 200; unknown 404; JSON catalogue for Lyon. Observe Method, Status, Content-Type and Location headers in the browser Network panel. Stop the server with Ctrl+C; in its terminal, return to pack root:

~~~powershell
Pop-Location
~~~

If port 8000 is occupied, run on 8001 and change the URLs above accordingly. Only Django's generated internal apps need the initial migrations; no custom business migrations should be created here.

## Section 2 first debugging checkpoint

~~~powershell
Push-Location .\deskhive-lab1
& ..\.venv\Scripts\python.exe booking.py
& ..\.venv\Scripts\python.exe -m unittest -v test_booking.py
& ..\.venv\Scripts\python.exe -m pdb booking.py
~~~

In pdb: n steps over, s steps into, p expression inspects, l lists source, w shows the stack, c continues and q quits. After you fix the three planted bugs, the demo should print 30.00, False and a rejected invalid interval. Its initial output is deliberately incorrect. After leaving pdb:

~~~powershell
Pop-Location
~~~

## Section 2 package and SQLite

~~~powershell
Push-Location .\deskhive-core
& ..\.venv\Scripts\python.exe -m unittest -v tests.test_booking
& ..\.venv\Scripts\python.exe bin/price_quote.py
& ..\.venv\Scripts\python.exe -m unittest discover -s tests -v
& ..\.venv\Scripts\python.exe bin/seed_db.py
& ..\.venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect('deskhive.db'); print(c.execute('SELECT name, hourly_rate FROM spaces ORDER BY id').fetchall()); c.close()"
Pop-Location
~~~

Expected for completed code: 19 rules tests, a 30.00 quote, 42 total package tests, and seed counts locations=3, spaces=6, bookings=5. The seed's default target is anchored to deskhive-core regardless of the current directory. An existing database is refused with exit code 2; choose a new path rather than deleting unrelated files:

~~~powershell
Push-Location .\deskhive-core
& ..\.venv\Scripts\python.exe bin/seed_db.py --database .\second-demo.db
Pop-Location
~~~

The optional sqlite3 CLI from the PDF is not required; Python's sqlite3 module is enough. Tests use memory/temporary databases and do not modify your demo database. Warnings about deliberately rejected bookings are normal test output.

## Installation lab reconstruction

To demonstrate project generation, choose a NEW empty directory outside the delivered packs. Invoke its Python after creating a venv and installing the same pinned requirements, then run:

~~~powershell
& .\.venv\Scripts\python.exe -m django startproject deskhive .
& .\.venv\Scripts\python.exe manage.py startapp spaces
& .\.venv\Scripts\python.exe manage.py startapp bookings
& .\.venv\Scripts\python.exe manage.py migrate
~~~

Before adding the app URLconf, the generated welcome page is visible. Register the two apps in settings, set Europe/Paris and compare against the supplied project. Never run startproject/startapp over delivered folders. The delivered pack is the recovery point, not a second feature set.

## Local Git checkpoints

From the pack root, after reviewing the supplied .gitignore:

~~~powershell
git init
git add .
git commit -m "Create DeskHive Django project"
~~~

Make later commits after public-page completion, booking repairs, packaging and SQLite completion. Git may ask you to set user.name/user.email; use your own identity. Do not commit .venv, caches, egg-info or databases.

## Troubleshooting

- py -3.12 unavailable: install Python 3.12 and re-run py -0p. A Python 3.9 interpreter cannot run this pack.
- ModuleNotFoundError django: install requirements with the exact .venv interpreter above.
- ModuleNotFoundError deskhive_core from bin: perform the editable install; running a bin script is intentionally a check of packaging.
- NoReverseMatch: compare app_name, named patterns and kwargs code against CONTRACT.md.
- 404 with uppercase LYO: the public URL contract uses lowercase lyo.
- POST 405 in the default test client: these public views are read-only. A real tokenless POST may be rejected earlier with 403 by CSRF middleware; the acceptance tests demonstrate both cases. Do not disable CSRF to change the response.
- HEAD 405 after a change: require_GET excludes HEAD; the reference uses require_safe.
- Starter 501 or failing acceptance tests: see the learner task list. These are deliberate tasks, not broken Django installation.
- Database locked: close the other interactive SQLite connection; the repository owns its connection and closes explicitly. Do not leave an interactive transaction open while calling add_booking.
- Seed already exists: choose a fresh --database target. No data are reset silently.
