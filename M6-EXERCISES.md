# DeskHive — M6 Serialization (student branch)

This branch already includes **working corrections from M4 and M5**. Do not redo them. The only new exercises are the two M6 labs below. Never use the instructor repository.

## Lab 1 — Serializing and Deserializing DeskHive Data with Serializer Classes

**Edit:** `deskhive-web/api_m6/serializers_intro.py` (the `SpaceSnapshotSerializer` TODO).

Use a **plain** `rest_framework.serializers.Serializer`, not `ModelSerializer`. Declare the existing `Space` fields explicitly:

- `code`: slug, at most 30 characters;
- `name`: text, at most 100 characters;
- `kind`: one of `desk` and `meeting_room`;
- `capacity`: integer, at least 1;
- `hourly_rate`: decimal, at most 7 digits total / 2 decimal places, strictly positive.

Practice serialization with an existing ORM `Space`, then deserialize a dictionary using `data=`, `is_valid()`, `.validated_data` and `.errors`. Try multiple spaces with `many=True`. No database insert, ModelSerializer or HTTP endpoint implementation is needed for Lab 1.

**Validation:** `python check.py --m6-lab1`. This command runs only the three tests for this exercise. They fail initially until you implement the TODO.

## Lab 2 — Building the DeskHive Booking REST API

**Edit:** `deskhive-web/api_m6/serializers.py` and `deskhive-web/api_m6/views.py`. The URLs are provided in `deskhive-web/api_m6/urls.py`.

1. Complete `SpaceSerializer(serializers.ModelSerializer)` with the six read-only output fields: `code`, `name`, `kind`, `capacity`, `hourly_rate`, `location_city` (`source='location.city'`).
2. Complete `SpaceListView` and `SpaceDetailView` using the M5 ORM catalogue. Retrieve a space using its `code` (not the numeric primary key). Endpoints: `GET /api/spaces/` and `GET /api/spaces/lyo-desk/`.
3. Implement `BookingCreateSerializer`, `BookingReadSerializer` and `BookingCreateView.post()` for `POST /api/bookings/`. Accept `space` code, `full_name`, `email`, `start`, and `end`. Validate the interval using existing DeskHive code (`bookings.intervals.local_interval` and `deskhive_core.booking.validate_booking`); **persist by calling `bookings.services.save_booking()`**, not an ORM shortcut. Return HTTP 201 on success and 400 on invalid booking data.
4. Preserve the existing session convention `m5_booking_ids` so that a booking created via API appears in M5's management page. Handle CSRF on browser/client POST requests.

**Validation:** `python check.py --m6` (Lab 1 and Lab 2). After finishing, also run `python check.py --all` to check earlier modules.

## Setup — PowerShell (Windows)

Use your existing clone or switch to the new branch:

```powershell
cd C:\dev\E4\deskhive-starter
git fetch origin
git switch m6-serialization
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .\deskhive-core
.\.venv\Scripts\python.exe check.py --m5
.\.venv\Scripts\python.exe check.py --m6-lab1
```

If `py` is unavailable, use a Python 3.12 executable to create `.venv`. After creating it, keep using the `.venv` interpreter.

## Setup — macOS/Linux

```bash
git fetch origin
git switch m6-serialization
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip install -e ./deskhive-core
./.venv/bin/python check.py --m5
./.venv/bin/python check.py --m6-lab1
```

The `--m5` checks should pass without editing the prior work. The M6 checks **intentionally fail before you complete their TODOs**. Do not edit the test files to make failures disappear.
