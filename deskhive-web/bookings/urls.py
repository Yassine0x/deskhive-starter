from django.urls import path
from . import views

app_name = "bookings"
urlpatterns = [
    path("request/", views.booking_request, name="request"),
    path("request/thanks/", views.booking_thanks, name="thanks"),
]
