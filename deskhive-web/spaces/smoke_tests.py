from django.test import TestCase

class StarterSmokeTests(TestCase):
    def test_home_runs(self):
        self.assertContains(self.client.get("/"), "DeskHive")

    def test_m4_pages_load_before_exercises(self):
        for url in ("/locations/", "/locations/lyo/", "/about/", "/bookings/request/", "/bookings/manage/", "/bookings/new/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
