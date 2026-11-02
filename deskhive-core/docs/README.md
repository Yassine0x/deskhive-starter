# Skeleton notes

The package directory is importable Python code. tests contains unittest tests, bin contains entry scripts, docs contains developer notes, and pyproject.toml declares how setuptools builds the distribution. An editable install lets changes in the package appear immediately to the installed interpreter. Test imports must use deskhive_core.booking after moving the standalone file into the package.

The database is created at runtime by bin/seed_db.py, never packaged with the source. Keep a single connection for an in-memory database. A transaction context commits or rolls back; explicitly close the repository to release resources. Record a reproduction, hypothesis, debugger observation, fix and regression test in your own debugging notes.
