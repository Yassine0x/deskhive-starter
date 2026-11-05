from django.test import Client, SimpleTestCase, TestCase
from .forms import BookingRequestForm
from .views import SESSION_KEY

def valid_data(**changes):
    data = {"full_name": "Ada Learner", "email": "ada@example.test", "space": "lyo-desk",
            "start": "2030-01-15T10:00", "end": "2030-01-15T11:30"}
    data.update(changes)
    return data

class RequestFormTests(TestCase):
    def test_valid_interval(self):
        form = BookingRequestForm(valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNotNone(form.cleaned_data["start"].utcoffset())

    def test_twelve_hours_and_past_dates_are_allowed(self):
        form = BookingRequestForm(valid_data(start="2020-01-15T00:00", end="2020-01-15T12:00"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_durations_have_global_errors(self):
        for end in ("2030-01-15T09:00", "2030-01-15T10:00", "2030-01-15T22:01"):
            with self.subTest(end=end):
                form = BookingRequestForm(valid_data(end=end))
                self.assertFalse(form.is_valid())
                self.assertIn("Duration must be positive", str(form.non_field_errors()))

    def test_bad_fields_are_rejected_without_crashing(self):
        for field, value in (("full_name", "  "), ("email", "bad"), ("space", "unknown"),
                             ("start", "wrong"), ("end", "")):
            with self.subTest(field=field):
                form = BookingRequestForm(valid_data(**{field: value}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_dst_ambiguous_and_nonexistent_times(self):
        for start, end in (("2030-03-31T02:30", "2030-03-31T04:00"),
                           ("2030-10-27T02:30", "2030-10-27T04:00")):
            with self.subTest(start=start):
                form = BookingRequestForm(valid_data(start=start, end=end))
                self.assertFalse(form.is_valid())
                self.assertIn("start", form.errors)

    def test_crossing_clock_change_is_explicitly_rejected(self):
        form = BookingRequestForm(valid_data(start="2030-03-31T01:00", end="2030-03-31T04:00"))
        self.assertFalse(form.is_valid())
        self.assertIn("clock change", str(form.non_field_errors()))

    def test_codes_cover_catalogue(self):
        from .catalogue import request_spaces
        from spaces.data import LOCATIONS
        spaces = request_spaces()
        self.assertEqual(len(spaces), 6)
        self.assertEqual({s["name"] for s in spaces.values()},
                         {s["name"] for loc in LOCATIONS.values() for s in loc["spaces"]})

class RequestFlowTests(TestCase):
    def test_get_is_unbound_and_does_not_store_request(self):
        response = self.client.get("/bookings/request/")
        self.assertTemplateUsed(response, "bookings/request.html")
        self.assertFalse(response.context["form"].is_bound)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'for="id_email"')

    def test_success_redirects_and_stores_only_summary(self):
        response = self.client.post("/bookings/request/", valid_data(hourly_rate="0", injected="x"))
        self.assertRedirects(response, "/bookings/request/thanks/")
        summary = self.client.session[SESSION_KEY]
        self.assertEqual(summary["space_name"], "Lyon Open Desk")
        self.assertEqual(summary["start"], "2030-01-15T10:00:00+01:00")
        self.assertNotIn("hourly_rate", summary)
        self.assertNotIn("injected", summary)
        self.assertContains(self.client.get(response.url), "No reservation has been created")
        self.assertEqual(self.client.session[SESSION_KEY], summary)

    def test_invalid_post_redisplays_values_and_field_errors(self):
        response = self.client.post("/bookings/request/", valid_data(email="bad"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ada Learner")
        self.assertContains(response, "Enter a valid email address")
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_empty_post_is_bound(self):
        response = self.client.post("/bookings/request/", {})
        self.assertTrue(response.context["form"].is_bound)
        self.assertEqual(len(response.context["form"].errors.keys() - {"__all__"}), 5)

    def test_invalid_interval_does_not_replace_previous_summary(self):
        self.client.post("/bookings/request/", valid_data())
        before = self.client.session[SESSION_KEY]
        response = self.client.post("/bookings/request/", valid_data(end="2030-01-15T09:00"))
        self.assertContains(response, "Duration must be positive")
        self.assertEqual(self.client.session[SESSION_KEY], before)

    def test_confirmation_is_private_to_session_and_escaped(self):
        response = self.client.post("/bookings/request/", valid_data(full_name='<script>alert("x")</script>'))
        self.assertEqual(response.status_code, 302)
        page = self.client.get(response.url)
        self.assertContains(page, "&lt;script&gt;")
        self.assertNotContains(page, "<script>")
        self.assertRedirects(Client().get(response.url), "/bookings/request/")

    def test_methods_and_csrf(self):
        self.assertEqual(self.client.put("/bookings/request/").status_code, 405)
        self.assertEqual(self.client.post("/bookings/request/thanks/").status_code, 405)
        self.assertEqual(self.client.head("/bookings/request/").content, b"")
        browser = Client(enforce_csrf_checks=True)
        self.assertEqual(browser.post("/bookings/request/", valid_data()).status_code, 403)
        browser.get("/bookings/request/")
        data = valid_data(csrfmiddlewaretoken=browser.cookies["csrftoken"].value)
        self.assertEqual(browser.post("/bookings/request/", data).status_code, 302)
