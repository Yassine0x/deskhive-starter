from unittest.mock import patch
from django.test import Client, SimpleTestCase
from django.urls import resolve, reverse
from .data import LOCATIONS
from .views import AboutView


class PublicPagesTests(SimpleTestCase):
    """Prohibit DB access: section 1 must work with in-memory data alone."""

    def test_home_has_reversed_navigation(self):
        response = self.client.get(reverse("spaces:home"))
        self.assertContains(response, "DeskHive")
        self.assertContains(response, f'href="{reverse("spaces:location_list")}"')
        self.assertContains(response, "does not accept bookings yet")

    def test_list_includes_every_location(self):
        response = self.client.get(reverse("spaces:location_list"))
        for code, location in LOCATIONS.items():
            self.assertContains(response, location["city"])
            self.assertContains(response, reverse("spaces:location_detail", kwargs={"code": code}))

    def test_each_detail_includes_space_data(self):
        for code, location in LOCATIONS.items():
            with self.subTest(code=code):
                response = self.client.get(reverse("spaces:location_detail", kwargs={"code": code}))
                self.assertContains(response, location["city"])
                for space in location["spaces"]:
                    self.assertContains(response, space["name"])
                    self.assertContains(response, space["hourly_rate"])

    def test_summary_has_exact_contract(self):
        for code, location in LOCATIONS.items():
            with self.subTest(code=code):
                response = self.client.get(reverse("spaces:location_summary", kwargs={"code": code}))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["Content-Type"], "application/json")
                self.assertEqual(response.json(), {"code": code, **location})
                self.assertIsInstance(response.json()["spaces"][0]["hourly_rate"], str)

    def test_unknown_location_is_404_in_html_and_json(self):
        for name in ("location_detail", "location_summary"):
            self.assertEqual(self.client.get(reverse(f"spaces:{name}", kwargs={"code": "xyz"})).status_code, 404)

    def test_uppercase_code_is_unknown_on_web(self):
        self.assertEqual(self.client.get("/locations/LYO/").status_code, 404)

    def test_unknown_route_is_404(self):
        self.assertEqual(self.client.get("/missing/").status_code, 404)

    def test_location_detail_uses_slug_converter(self):
        match = resolve("/locations/lyo/")
        self.assertEqual(match.view_name, "spaces:location_detail")
        self.assertEqual(match.kwargs, {"code": "lyo"})

    def test_about_is_class_based(self):
        self.assertIs(resolve(reverse("spaces:about")).func.view_class, AboutView)
        self.assertContains(self.client.get(reverse("spaces:about")), "fictional coworking")

    def test_query_string_does_not_change_route(self):
        self.assertContains(self.client.get("/locations/lyo/?source=lesson"), "Lyon")

    def test_append_slash_redirect(self):
        self.assertRedirects(self.client.get("/locations"), "/locations/",
                             status_code=301, fetch_redirect_response=False)

    def test_read_only_routes_reject_post_and_accept_head(self):
        for url in ("/", "/locations/", "/locations/lyo/",
                    "/locations/lyo/summary.json", "/about/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 405)
                response = self.client.head(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"")
                # The default test client skips CSRF. Real tokenless POSTs stop in middleware.
                self.assertEqual(Client(enforce_csrf_checks=True).post(url).status_code, 403)

    def test_catalogue_values_are_html_escaped(self):
        location = {"city": '<script>alert("x")</script>', "address": "A & B", "spaces": []}
        with patch.dict(LOCATIONS, {"test": location}):
            response = self.client.get("/locations/test/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")

    def test_no_later_module_endpoints(self):
        for url in ("/bookings/", "/api/", "/admin/"):
            self.assertEqual(self.client.get(url).status_code, 404)
