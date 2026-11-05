# M4 — Templates and Forms: focused labs

Start with M4-README.md. Keep your earlier M1/M2 work on its original branch.
Supplied: routing, catalogue, rendered views, shared layout, form fields/widgets, CSRF,
session/redirect workflow, timezone adapter and corrected M2 pure rules.
All M1/M2 exercises, including the former optional SQLite exercises, are already corrected in this M4 checkpoint. Only the M4 tasks below remain to complete.

## Lab: Building the DeskHive Site Layout with Template Inheritance

First read spaces/views.py, templates/base.html, templates/partials/navigation.html,
and spaces/templates/spaces/home.html under deskhive-web. Observe the Template/Context demonstration.
The supplied home page is the worked example; reproduce its inheritance pattern, not its content.

Complete these two existing files under deskhive-web/spaces/templates/spaces/:

1. location_list.html: inherit base.html; override title and content; loop over locations.items;
   show cities/addresses; generate spaces:location_detail URLs with code; display
   "No locations available." for an empty catalogue.
2. location_detail.html: inherit base.html; show location.city and address; count spaces with
   length/pluralize; loop over location.spaces; show name, kind, capacity and the original hourly_rate;
   link spaces:location_summary using code; display "No spaces available." for an empty list.

Keep automatic escaping. Do not use safe, hard-coded cities, literal URLs or database queries.
Verify with the venv Python: deskhive-web/manage.py test spaces.tests spaces.test_m4.

## Lab: Creating and Validating the DeskHive Booking Request Form

Read bookings/forms.py and trace bookings/views.py through GET, invalid POST and valid POST.
Inspect templates/bookings/request.html and the shared form_field.html partial: labels,
widgets, field errors, global errors and csrf_token must all be visible.

Complete only BookingRequestForm.clean in deskhive-web/bookings/forms.py:

1. Call super().clean(); retrieve start and end safely (invalid fields may be absent).
2. When both exist, use the supplied local_interval adapter.
3. Call the imported validate_booking once with those local naive dates.
4. Translate InvalidBookingError into forms.ValidationError, keeping the original cause.
5. Return the cleaned data. Remove the temporary exercise rejection.

Do not add future-date or opening-hours rules. Keep helpers, fields, tests and view workflow intact.
Verify with the venv Python: deskhive-web/manage.py test bookings.tests.
Final check: check.py --m4. Demonstrate invalid email, reversed dates and a valid confirmation.
Show that refreshing confirmation does not create a reservation and another browser session cannot see it.

Deliver the three completed files and the --m4 test result. No SQLite extension is required.
