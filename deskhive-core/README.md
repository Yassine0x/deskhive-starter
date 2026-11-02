# DeskHive core

Python 3.12 package for section 2: pure booking rules and a three-table SQLite repository. From this folder, use the parent virtual environment and install this package with an editable install before running scripts under bin. Full commands are in ../WINDOWS.md; behaviour is fixed in ../CONTRACT.md.

Folders: deskhive_core holds importable code; tests contains behavioural acceptance tests; bin holds runnable demonstrations; docs explains the skeleton. __version__ is 0.1.0. pyproject.toml deliberately matches the original exercise.

Run ../.venv/Scripts/python.exe -m unittest discover -s tests -v after installation. A completed implementation has 42 passing tests. The seed needs sibling ../deskhive-web/spaces/data.py; retain the complete pack layout. No Django dependency is imported by this package.
