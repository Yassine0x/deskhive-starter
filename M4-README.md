# M4 — Templates and Forms: code checkpoint

This branch follows M1/M2 and does not implement M5. Read M4-EXERCISES.md for the learner tasks.
The official syllabus calls this topic Module 03; our course label remains M4.

## Contract

- Catalogue: the existing LOCATIONS dictionary, three locations and six spaces. M1 URLs, case sensitivity, JSON keys, escaping and read-only methods remain unchanged.
- Four HTML views use templates with a shared base and navigation. About remains class-based.
- GET /bookings/request/ displays an unbound Form; POST validates it. Fields: full_name, email, space, start, end. Stable space codes are declared in bookings/catalogue.py; the M1 JSON is unchanged.
- Valid POST redirects (302) to /bookings/request/thanks/. Invalid POST renders the bound form (200), preserving input and displaying field/global errors. CSRF remains enabled.
- Confirmation stores only an allowlisted JSON-serializable summary in the visitor's Django session, expiring after 30 minutes. Refresh does not submit again. No summary means redirect to the form.
- No booking, email delivery, availability guarantee, ORM business model or prototype SQLite access. Django's internal session tables require migrate.
- Dates are entered in Europe/Paris, with USE_TZ=True. Django rejects ambiguous/nonexistent local times. The supplied adapter rejects an interval with different endpoint UTC offsets, then explicitly converts to local naive dates for the M2 validator. Positive duration <=12h; no future-date, opening-hours or attendance rule.
- Prices and other unexpected POST keys are not trusted or stored. Request confirmation is not a reservation.

## Windows commands (from THIS repository root)

Use Python 3.12, not whichever global version happens to be installed. Each repository needs its own environment.

```powershell
python --version  # must be 3.12.x before the next command
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pip install --no-build-isolation -e .\deskhive-core
& .\.venv\Scripts\python.exe deskhive-web/manage.py migrate
& .\.venv\Scripts\python.exe check.py --m4
& .\.venv\Scripts\python.exe deskhive-web/manage.py runserver
```

On macOS use python3.12 to create the venv and ./.venv/bin/python for subsequent commands.

## Tests and scope

--m4 runs catalogue regression, template and form/session tests, independently of optional SQLite methods.
--web runs spaces and bookings; --all additionally runs the core suite.
On the starter, --smoke must pass before exercises; --m4 intentionally fails until the three TODO files are completed.
The M4 starter supplies all earlier M1/M2 exercises corrected, including the three SQLite methods. No earlier bug or TODO remains to complete. Private instructor guides are not included. Only the new M4 exercises remain unfinished. Run --core to verify the 42 completed core tests; --all becomes green after completing M4.
The old test excluding /bookings/, /admin/ and /api/ remains valid: M4 adds only the two explicit request URLs, not those roots.

## Short demonstration before the template lab

From the root run the venv Python with deskhive-web/manage.py shell, then:

```python
from django.template import Template, Context
t = Template("{{ city|upper }}: {{ count }} space{{ count|pluralize }}")
t.render(Context({"city": "Lyon", "count": 2}))
```

Explain reuse, context, escaping, tags versus filters and render before editing templates.
For forms, demonstrate a separate one-field contact form, is_bound/is_valid/cleaned_data, then cross-field errors before assigning the request validation task.
Full lessons, slides, quiz imports and instructor script are separate future deliverables.
