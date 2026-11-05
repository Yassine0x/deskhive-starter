from .models import Location

def locations():
    return {location.code: {'city': location.city, 'address': location.address,
            'spaces': [{'name': s.name, 'kind': s.kind, 'capacity': s.capacity, 'hourly_rate': str(s.hourly_rate)}
                       for s in location.spaces.all()]}
            for location in Location.objects.prefetch_related('spaces').order_by('created_at', 'code')}
