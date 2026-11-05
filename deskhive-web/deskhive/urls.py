from django.urls import include, path

urlpatterns = [
    path("", include("spaces.urls")),
    path("bookings/", include("bookings.urls")),
]
