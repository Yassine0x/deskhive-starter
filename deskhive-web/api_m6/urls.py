from django.urls import path
from django.views.decorators.csrf import csrf_protect
from .views import SpaceListView, SpaceDetailView, BookingCreateView

app_name = 'api_m6'
urlpatterns = [
    path('spaces/', SpaceListView.as_view(), name='spaces-list'),
    path('spaces/<slug:code>/', SpaceDetailView.as_view(), name='spaces-detail'),
    path('bookings/', csrf_protect(BookingCreateView.as_view()), name='bookings-create'),
]
