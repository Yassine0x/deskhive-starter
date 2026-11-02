from django.test import SimpleTestCase
from django.urls import reverse

class StarterSmokeTests(SimpleTestCase):
    def test_home_runs(self):
        self.assertContains(self.client.get(reverse("spaces:home")), "DeskHive")

    def test_incomplete_views_are_explicit(self):
        for url in ("/locations/", "/locations/lyo/", "/locations/lyo/summary.json", "/about/"):
            self.assertEqual(self.client.get(url).status_code, 501)
