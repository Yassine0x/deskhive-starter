
"""M6 REST endpoints. The booking write reuses the M5 transactional service."""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from spaces.models import Space

from .serializers import (
    SpaceSerializer,
    BookingCreateSerializer,
    BookingReadSerializer,
)


class SpaceListView(generics.ListAPIView):
    serializer_class = SpaceSerializer
    queryset = Space.objects.select_related('location').order_by('code')


class SpaceDetailView(generics.RetrieveAPIView):
    serializer_class = SpaceSerializer
    queryset = Space.objects.select_related('location')
    lookup_field = 'code'


@method_decorator(csrf_protect, name='dispatch')
class BookingCreateView(APIView):
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        owned = request.session.get('m5_booking_ids', [])
        request.session['m5_booking_ids'] = list(set(owned + [booking.pk]))
        return Response(
            BookingReadSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )
