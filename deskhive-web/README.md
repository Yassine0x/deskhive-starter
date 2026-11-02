# DeskHive public pages

Section 1 only: generated Django project deskhive, apps spaces/bookings, and five public routes. Business data remain in spaces/data.py. See ../WINDOWS.md and ../CONTRACT.md. No business models, forms or templates are required. Default generated Django settings/middleware and internal migrations are retained to inspect framework features.

Run manage.py check, migrate, test spaces and runserver with the parent's venv interpreter. A completed implementation has 14 passing tests and all five public routes work. JsonResponse is used only for the specified location summary, not a later REST API.
