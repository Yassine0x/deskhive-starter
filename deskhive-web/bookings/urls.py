from django.urls import path
from . import views, views_m5

app_name = "bookings"
urlpatterns = [
    path('manage/', views_m5.booking_list, name='manage'),
    path('new/', views_m5.booking_edit, name='create'),
    path('<int:pk>/edit/', views_m5.booking_edit, name='edit'),
    path('<int:pk>/delete/', views_m5.booking_delete, name='delete'),
    path('availability/', views_m5.availability, name='availability'),
    path("request/", views.booking_request, name="request"),
    path("request/thanks/", views.booking_thanks, name="thanks"),
]
