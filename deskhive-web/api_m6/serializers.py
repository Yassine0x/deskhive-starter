"""M6 Lab 2: complete serializers using the existing M5 ORM and rules."""
from rest_framework import serializers
from spaces.models import Space

class SpaceSerializer(serializers.ModelSerializer):
    # TODO M6 Lab 2: read-only location_city from location.city.
    class Meta:
        model = Space
        # TODO M6 Lab 2: expose code, name, kind, capacity,
        # hourly_rate and location_city as read-only data.
        fields = ('code', 'name', 'kind', 'capacity', 'hourly_rate')

class BookingCreateSerializer(serializers.Serializer):
    # TODO M6 Lab 2: declare space (lookup by code), full_name, email,
    # start and end. Validate interval with local_interval + validate_booking.
    # Implement create() by calling bookings.services.save_booking.
    # Translate model/service validation failures into DRF ValidationError.
    pass

class BookingReadSerializer(serializers.Serializer):
    # TODO M6 Lab 2: return id, space code, start and end (read-only).
    pass
