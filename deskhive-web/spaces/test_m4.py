from unittest.mock import patch
from django.template import Context, Template
from django.test import TestCase
from .data import LOCATIONS

class TemplateTests(TestCase):
    def test_pages_use_shared_layout_and_named_templates(self):
        for url, name in (("/", "home"), ("/locations/", "location_list"),
                          ("/locations/lyo/", "location_detail"), ("/about/", "about")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, f"spaces/{name}.html")
                self.assertTemplateUsed(response, "base.html")
                self.assertTemplateUsed(response, "partials/navigation.html")
                self.assertContains(response, 'href="/bookings/request/"')

    def test_empty_catalogue_and_space_list(self):
        with patch("spaces.views.locations", return_value={}):
            self.assertContains(self.client.get("/locations/"), "No locations available")
        with patch("spaces.views.locations", return_value={"empty": {"city": "Empty", "address": "", "spaces": []}}):
            self.assertContains(self.client.get("/locations/empty/"), "No spaces available")

    def test_template_object_context_filter_and_escaping(self):
        template = Template("{{ city|upper }}: {{ count }} space{{ count|pluralize }}")
        self.assertEqual(template.render(Context({"city": "Lyon", "count": 2})), "LYON: 2 spaces")
        self.assertIn("&lt;", template.render(Context({"city": "<x>", "count": 1})))
