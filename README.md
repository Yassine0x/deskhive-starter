# M5 checkpoint

See [M5-README.md](M5-README.md) and [M5-EXERCISES.md](M5-EXERCISES.md) for the active branch. Historical sections below describe earlier modules.

# Active branch: M4 — Templates and Forms

Start with [M4-README.md](M4-README.md) and [M4-EXERCISES.md](M4-EXERCISES.md). The M1/M2 instructions below are historical for this branch.

# deskhive-starter

Student starting point: the home page works, four unfinished views return 501, and the booking/SQLite exercises deliberately contain bugs and TODOs.

DeskHive is a fictional coworking company in Lyon, Lille and Barcelona. This repository covers only these sections, in the LMS order:

1. Introduction to Django Web Framework: views, URL mapping and an in-memory catalogue.
2. Debugging, Databases and Project Skeletons: booking rules, an installable Python package and SQLite CRUD.

## 1 Prerequisites on each computer

Install **Python 3.12**, **Git**, and an editor such as VS Code or PyCharm. Use the same Python minor version on Windows and macOS. Internet access is needed for the first dependency installation; the site and exercises then run locally.

- Windows: [Python installation documentation](https://docs.python.org/3.12/using/windows.html). Verify `py -3.12 --version`. If only Python 3.9 appears, install Python 3.12 before proceeding. If the launcher is unavailable but `python --version` is 3.12.x, use `python -m venv .venv` instead.
- macOS Intel or Apple Silicon: [Python installation documentation](https://docs.python.org/3.12/using/mac.html). Install Python 3.12, then verify `python3.12 --version`. Do not assume the system's `python3` is the required version. An existing Homebrew setup can use `brew install python@3.12`.
- Both: verify `git --version`. On macOS, if Git requests Apple's Command Line Tools, finish that installation before cloning. VS Code is optional; the commands below need only a terminal.

The repository includes pinned dependencies in requirements.txt. Do not copy a virtual environment from another machine: create one on every computer. No Docker, database server, frontend build, DRF or jQuery is needed.

## 2 Get the project

After the repository has been published, copy its actual HTTPS address from GitHub's **Code** button. Replace `URL_DU_DEPOT` below with that address before running:

~~~text
git clone URL_DU_DEPOT deskhive-starter
cd deskhive-starter
~~~

If you already have this folder locally, open a terminal in it and skip cloning. You must see requirements.txt, check.py and the deskhive-web and deskhive-core folders. All installation commands below start from this repository root.

## 3 Install on Windows PowerShell

~~~powershell
py -3.12 --version
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& .\.venv\Scripts\python.exe -m pip install --no-build-isolation -e .\deskhive-core
& .\.venv\Scripts\python.exe -c "import deskhive_core; print(deskhive_core.__version__)"
& .\.venv\Scripts\python.exe .\check.py --smoke
~~~

Expected package version: **0.1.0**. Expected: 2 Web smoke tests and 1 core smoke test pass. Acceptance tests are deliberately red until you complete the exercises. Start with [EXERCISES.md](EXERCISES.md).

The interpreter is called directly. You do not need to activate the environment or change PowerShell execution policy. The editable install lets scripts in bin import the local core package; the packaging concepts are explained in section 2.

## 4 Install on macOS Terminal

~~~bash
python3.12 --version
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip install --no-build-isolation -e ./deskhive-core
./.venv/bin/python -c "import deskhive_core; print(deskhive_core.__version__)"
./.venv/bin/python check.py --smoke
~~~

The expected results are the same as on Windows. Do not use sudo pip. If pip reports a certificate verification error with the python.org installer, run **Install Certificates.command** in the Applications/Python 3.12 folder, then retry. No activation is required.

## 5 Start the Web site

Windows PowerShell, from the repository root:

~~~powershell
cd .\deskhive-web
& ..\.venv\Scripts\python.exe manage.py check
& ..\.venv\Scripts\python.exe manage.py migrate
& ..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
~~~

macOS Terminal, from the repository root:

~~~bash
cd deskhive-web
../.venv/bin/python manage.py check
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py runserver 127.0.0.1:8000
~~~

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The command keeps running: leave this terminal open. Press **Ctrl+C** to stop. Then run `cd ..` to return to the repository root. If port 8000 is occupied, use `127.0.0.1:8001` in the command and browser address.

Public routes: `/`, `/locations/`, `/locations/lyo/`, `/locations/lyo/summary.json`, `/about/`. The last four routes return 501 until implemented; this means exercise work remains, not an installation error.

The site has no booking form or database-backed catalogue yet. Django's db.sqlite3 holds its generated internal tables; the later SQL exercise uses a separate deskhive.db.

## 6 Run tests and section 2 exercises

Run these commands from the repository root in a second terminal, or after stopping the server and returning with `cd ..`.

| Purpose | Windows PowerShell | macOS Terminal |
|---|---|---|
| Untouched starter preflight | `& .\.venv\Scripts\python.exe check.py --smoke` | `./.venv/bin/python check.py --smoke` |
| Web acceptance | `& .\.venv\Scripts\python.exe check.py --web` | `./.venv/bin/python check.py --web` |
| Booking rules tests | `& .\.venv\Scripts\python.exe check.py --rules` | `./.venv/bin/python check.py --rules` |
| Packaged rules and SQLite tests | `& .\.venv\Scripts\python.exe check.py --core` | `./.venv/bin/python check.py --core` |
| All acceptance tests | `& .\.venv\Scripts\python.exe check.py --all` | `./.venv/bin/python check.py --all` |
| Debug booking rules | `& .\.venv\Scripts\python.exe -m pdb .\deskhive-core\deskhive_core\booking.py` | `./.venv/bin/python -m pdb deskhive-core/deskhive_core/booking.py` |
| Price quote | `& .\.venv\Scripts\python.exe .\deskhive-core\bin\price_quote.py` | `./.venv/bin/python deskhive-core/bin/price_quote.py` |
| Seed a NEW database | `& .\.venv\Scripts\python.exe .\deskhive-core\bin\seed_db.py` | `./.venv/bin/python deskhive-core/bin/seed_db.py` |

Before completion: rule tests fail for the three planted defects; DB tests raise NotImplementedError for three methods. The quote is wrong and the seed cannot complete until the relevant tasks are fixed. The --smoke checks assert the original 501 starter state; use --all, not --smoke, to validate completed work. The CI workflow intentionally checks only --smoke for this original distribution; change its command to --all in your own completed submission.

The seed refuses to overwrite an existing file. Choose another target, for example append `--database deskhive-core/demo-2.db` to the root-level seed command. Keep deskhive-web and deskhive-core together: the seed reads the single catalogue at deskhive-web/spaces/data.py using a path relative to its own file.

Edit only `deskhive-core/deskhive_core/booking.py` for the three booking fixes. Its tests live in `deskhive-core/tests/test_booking.py`. The existing package is the single source of booking rules: fix it once, then use it for the packaging and SQLite exercises. No file needs to be copied or moved.

Read [CONTRACT.md](CONTRACT.md) before changing signatures, fields, URL names or rules. The full assignment steps are in [EXERCISES.md](EXERCISES.md); its longer command examples use PowerShell, while the equivalents for macOS are all given above.

## 7 Continue your work on another computer

If you save your work in your own Git repository, commit and push the changes you want to transfer. On the other computer, clone that repository and follow the Windows or macOS installation steps above.

Create a new virtual environment on each computer. Git transfers source code, not the installed dependencies or local SQLite databases. Run Django's migrations again. Once you have completed the SQLite exercise, you can also run the seed script to recreate its example data.

Use the checks appropriate to your progress: --smoke applies only to the untouched starter; --web and --core check the corresponding exercises; --all validates the completed project. Incomplete exercises are expected to fail their acceptance tests.

Before pulling changes into an existing clone, stop the server and commit or stash your local edits. Reinstall dependencies if requirements.txt has changed.

## 8 Troubleshooting

- Python command missing: finish installing Python 3.12 and reopen the terminal. On Windows check `py -0p`; on Mac check `python3.12 --version`.
- Wrong working directory: return to this repository root before using check.py or installing dependencies.
- ModuleNotFoundError django/deskhive_core: install with the .venv interpreter, including the editable core command. Do not use global pip.
- Site cannot be reached: leave runserver running and use the exact displayed port.
- POST gives 403/405: pages are read-only. CSRF middleware rejects tokenless POST with 403 before the view; view-level method checks return 405. Do not disable CSRF.
- Unknown uppercase code LYO: public URLs use lowercase lyo; SQLite seed normalizes codes to uppercase.
- SQLite command-line tool missing: it is optional; Python's sqlite3 is sufficient.
- Windows path with spaces: use quoted paths in cd; the provided relative commands work from the repository root.

## Repository contents and portability

Only source, documentation and pinned dependencies are tracked. .gitignore excludes .venv, caches, database files, .DS_Store and local IDE state. The included GitHub Actions workflow checks the original starter on Windows and macOS; its results are available in the repository's Actions tab.
