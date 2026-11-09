from datetime import datetime
from zoneinfo import ZoneInfo
from django.test import TestCase, Client
from spaces.models import Space
from bookings.models import Booking, Member

def payload(**kw):
    data = {'space': 'lyo-desk', 'full_name': 'Ada Learner', 'email': 'ADA@example.test',
            'start': '2030-01-15T10:00:00+01:00', 'end': '2030-01-15T11:00:00+01:00'}
    data.update(kw)
    return data

class SerializerBasicsTests(TestCase):
    """M6 Lab 1 acceptance checks: plain serializers.Serializer."""

    def test_plain_serializer_reads_real_space(self):
        from api_m6.serializers_intro import SpaceSnapshotSerializer
        space = Space.objects.get(code='lyo-desk')
        output = SpaceSnapshotSerializer(space).data
        self.assertEqual(output['code'], 'lyo-desk')
        self.assertEqual(output['kind'], 'desk')
        self.assertEqual(output['capacity'], space.capacity)
        self.assertEqual(output['hourly_rate'], str(space.hourly_rate))

    def test_plain_serializer_validates_input_without_persisting(self):
        from decimal import Decimal
        from api_m6.serializers_intro import SpaceSnapshotSerializer
        count_before = Space.objects.count()
        data = {'code': 'new-desk', 'name': 'New desk', 'kind': 'desk',
                'capacity': 2, 'hourly_rate': '13.50'}
        serializer = SpaceSnapshotSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['hourly_rate'], Decimal('13.50'))
        self.assertEqual(serializer.data['code'], 'new-desk')
        self.assertEqual(Space.objects.count(), count_before)

    def test_plain_serializer_rejects_invalid_input(self):
        from api_m6.serializers_intro import SpaceSnapshotSerializer
        data = {'code': 'bad', 'name': 'Broken', 'kind': 'other',
                'capacity': 0, 'hourly_rate': '-1.00'}
        serializer = SpaceSnapshotSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('kind', serializer.errors)
        self.assertIn('capacity', serializer.errors)
        self.assertIn('hourly_rate', serializer.errors)


class SerializationTests(TestCase):
    def test_space_list_and_detail_use_orm(self):
        Space.objects.filter(code='lyo-desk').update(hourly_rate='19.50')
        r = self.client.get('/api/spaces/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 6)
        r = self.client.get('/api/spaces/lyo-desk/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['hourly_rate'], '19.50')
        self.assertEqual(r.json()['location_city'], 'Lyon')
        self.assertEqual(self.client.get('/api/spaces/does-not-exist/').status_code, 404)
        self.assertEqual(self.client.post('/api/spaces/', data=payload()).status_code, 405)

    def test_booking_post_saves_using_existing_service_and_m5_session(self):
        response = self.client.post('/api/bookings/', data=payload(), content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['space'], 'lyo-desk')
        self.assertEqual(Member.objects.get().email, 'ada@example.test')
        booking = Booking.objects.get()
        self.assertIn(booking.pk, self.client.session['m5_booking_ids'])
        self.assertContains(self.client.get('/bookings/manage/'), 'Lyon Open Desk')

    def test_invalid_intervals_and_conflicts_return_400_without_partial_save(self):
        response = self.client.post('/api/bookings/', data=payload(), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        r = self.client.post('/api/bookings/', data=payload(email='other@example.test'), content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 1)
        for changes in [dict(end='2030-01-15T10:00:00+01:00'),
                        dict(end='2030-01-16T11:00:00+01:00'),
                        dict(space='unknown')]:
            with self.subTest(changes=changes):
                r = self.client.post('/api/bookings/', data=payload(**changes), content_type='application/json')
                self.assertEqual(r.status_code, 400)

    def test_adjacent_booking_is_accepted(self):
        self.client.post('/api/bookings/', data=payload(), content_type='application/json')
        r = self.client.post('/api/bookings/', data=payload(start='2030-01-15T11:00:00+01:00',end='2030-01-15T12:00:00+01:00'), content_type='application/json')
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(Booking.objects.count(), 2)

    def test_api_requires_csrf_on_real_post(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/bookings/', data=payload(),content_type='application/json').status_code,403)
        self.assertEqual(Booking.objects.count(),0)
