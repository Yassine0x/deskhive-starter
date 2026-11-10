from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from bookings.intervals import local_interval
from bookings.services import save_booking
from deskhive_core.booking import InvalidBookingError, validate_booking
from spaces.models import Space

class SpaceSerializer(serializers.ModelSerializer):
    location_city = serializers.CharField(source='location.city', read_only=True)
    class Meta:
        model = Space
        fields = ('code', 'name', 'kind', 'capacity', 'hourly_rate', 'location_city')
        read_only_fields = fields

class BookingCreateSerializer(serializers.Serializer):
    space = serializers.SlugRelatedField(slug_field='code', queryset=Space.objects.all())
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, data):
        try:
            validate_booking(*local_interval(data['start'], data['end']))
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        except (InvalidBookingError, ValueError) as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return data

    def create(self, validated_data):
        try:
            return save_booking(**validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'non_field_errors': exc.messages}) from exc

class BookingReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    space = serializers.CharField(source='space.code', read_only=True)
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)
