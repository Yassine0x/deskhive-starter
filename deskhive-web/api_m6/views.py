"""M6 Lab 2: expose the ORM catalogue and create bookings."""
from rest_framework import generics
from rest_framework.views import APIView
from spaces.models import Space
from .serializers import SpaceSerializer

class SpaceListView(generics.ListAPIView):
    serializer_class = SpaceSerializer
    # TODO M6 Lab 2: query the actual M5 ORM catalogue, with location.
    queryset = Space.objects.none()

class SpaceDetailView(generics.RetrieveAPIView):
    serializer_class = SpaceSerializer
    # TODO M6 Lab 2: queryset + lookup_field='code'.
    queryset = Space.objects.none()

class BookingCreateView(APIView):
    # TODO M6 Lab 2: POST deserialization, validation, serializer.save(),
    # preserve M5 session ownership ('m5_booking_ids'), return 201 + JSON.
    # Do not use Booking.objects.create().
    pass
