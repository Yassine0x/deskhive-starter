from datetime import datetime
from zoneinfo import ZoneInfo
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, Client
from spaces.models import Location, Space, TimestampedModel
from .models import Booking, Member
from .services import save_booking
from .forms_m5 import PersistentBookingForm

ZONE = ZoneInfo('Europe/Paris')

def payload(**changes):
    values = dict(space='lyo-desk', full_name='Ada Learner', email='ada@example.test',
                  start='2030-01-15T10:00', end='2030-01-15T11:00')
    values.update(changes)
    return values

class ModelAndORMTests(TestCase):
    def save(self, **changes):
        form = PersistentBookingForm(payload(**changes))
        self.assertTrue(form.is_valid(), form.errors)
        return save_booking(**form.cleaned_data)

    def test_seed_and_keys_and_abstract_inheritance(self):
        self.assertEqual(Location.objects.count(), 3)
        self.assertEqual(Space.objects.count(), 6)
        self.assertTrue(TimestampedModel._meta.abstract)
        self.assertEqual(Location.objects.get(pk='lyo').city, 'Lyon')
        self.assertIsInstance(Space.objects.first().pk, int)

    def test_create_read_update_delete(self):
        booking = self.save()
        self.assertEqual(Booking.objects.get(pk=booking.pk).member.email, 'ada@example.test')
        form = PersistentBookingForm(payload(start='2030-01-15T11:00', end='2030-01-15T12:00'))
        self.assertTrue(form.is_valid())
        save_booking(**form.cleaned_data, booking=booking)
        booking.refresh_from_db()
        self.assertEqual(booking.start.astimezone(ZONE).hour, 11)
        booking.delete()
        self.assertEqual(Booking.objects.count(), 0)

    def test_overlap_rejected_but_adjacent_allowed(self):
        self.save()
        for start, end in [('10:00', '11:00'), ('09:30', '10:30'), ('10:30', '11:30'), ('09:00', '12:00')]:
            with self.subTest(start=start), self.assertRaises(ValidationError):
                self.save(start='2030-01-15T'+start, end='2030-01-15T'+end)
        self.save(start='2030-01-15T11:00', end='2030-01-15T12:00')
        self.save(space='lyo-room')
        self.assertEqual(Booking.objects.count(), 3)

    def test_rejected_write_rolls_back_member(self):
        self.save()
        with self.assertRaises(ValidationError):
            self.save(email='other@example.test')
        self.assertEqual(Member.objects.count(), 1)

    def test_booking_update_excludes_itself(self):
        booking = self.save()
        booking.full_clean()

    def test_space_constraints(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Space.objects.filter(code='lyo-desk').update(capacity=0)

    def test_invalid_intervals_and_dst(self):
        for changes in [dict(end='2030-01-15T10:00'), dict(end='2030-01-15T23:00'),
                        dict(start='2030-03-31T02:30', end='2030-03-31T04:00'),
                        dict(start='2030-03-31T01:00', end='2030-03-31T04:00')]:
            self.assertFalse(PersistentBookingForm(payload(**changes)).is_valid())

    def test_http_catalogue_reads_database(self):
        Space.objects.filter(code='lyo-desk').update(hourly_rate='17.50')
        response = self.client.get('/locations/lyo/summary.json')
        self.assertEqual(response.json()['spaces'][0]['hourly_rate'], '17.50')

class BookingHTTPTests(TestCase):
    def test_create_list_edit_delete(self):
        self.assertRedirects(self.client.post('/bookings/new/', payload()), '/bookings/manage/')
        booking = Booking.objects.get()
        self.assertContains(self.client.get('/bookings/manage/'), 'Lyon Open Desk')
        self.assertRedirects(self.client.post(f'/bookings/{booking.pk}/edit/', payload(end='2030-01-15T12:00')), '/bookings/manage/')
        booking.refresh_from_db()
        self.assertEqual(booking.end.astimezone(ZONE).hour, 12)
        self.assertEqual(self.client.get(f'/bookings/{booking.pk}/delete/').status_code, 405)
        self.assertRedirects(self.client.post(f'/bookings/{booking.pk}/delete/'), '/bookings/manage/')
        self.assertFalse(Booking.objects.exists())

    def test_other_session_cannot_edit_or_delete(self):
        self.client.post('/bookings/new/', payload())
        pk = Booking.objects.get().pk
        other = Client()
        self.assertEqual(other.post(f'/bookings/{pk}/edit/', payload()).status_code, 404)
        self.assertEqual(other.post(f'/bookings/{pk}/delete/').status_code, 404)
        self.assertNotContains(other.get('/bookings/manage/'), 'Ada Learner')

    def test_conflict_preserves_input_and_does_not_create(self):
        self.client.post('/bookings/new/', payload())
        response = self.client.post('/bookings/new/', payload(full_name='Second learner'))
        self.assertContains(response, 'already booked')
        self.assertContains(response, 'Second learner')
        self.assertEqual(Booking.objects.count(), 1)

    def test_availability_contract_invalid_and_read_only(self):
        self.assertEqual(self.client.get('/bookings/availability/').status_code, 400)
        self.assertEqual(self.client.post('/bookings/availability/', payload()).status_code, 405)
        self.assertEqual(self.client.get('/bookings/availability/', payload()).json(), {'available': True})
        self.client.post('/bookings/new/', payload())
        response = self.client.get('/bookings/availability/', payload())
        self.assertEqual(response.json(), {'available': False})
        self.assertIn('no-store', response.headers['Cache-Control'])
        self.assertEqual(self.client.get('/bookings/availability/', payload(start='2030-01-15T11:00', end='2030-01-15T12:00')).json(), {'available': True})

    def test_csrf_create_and_delete(self):
        browser = Client(enforce_csrf_checks=True)
        self.assertEqual(browser.post('/bookings/new/', payload()).status_code, 403)
        browser.get('/bookings/new/')
        token = browser.cookies['csrftoken'].value
        self.assertEqual(browser.post('/bookings/new/', payload(csrfmiddlewaretoken=token)).status_code, 302)
        pk = Booking.objects.get().pk
        self.assertEqual(browser.post(f'/bookings/{pk}/delete/').status_code, 403)

    def test_jquery_and_accessible_details_are_wired(self):
        response = self.client.get('/bookings/manage/')
        self.assertContains(response, 'aria-expanded="false"', count=6)
        self.assertContains(response, 'jquery-3.7.1.min.js')
        self.assertContains(self.client.get('/bookings/new/'), 'aria-live="polite"')
