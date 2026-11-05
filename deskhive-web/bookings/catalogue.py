"""Stable public codes backed by Django ORM; data.py is historical seed input."""
from spaces.models import Space

def request_spaces():
    return {s.code: {'name': s.name, 'kind': s.kind, 'capacity': s.capacity,
                     'hourly_rate': str(s.hourly_rate), 'city': s.location.city}
            for s in Space.objects.select_related('location')}
