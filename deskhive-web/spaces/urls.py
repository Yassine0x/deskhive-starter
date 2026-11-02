from django.urls import path
from . import views

app_name = "spaces"
urlpatterns = [
    path("", views.home, name="home"),
    path("locations/", views.location_list, name="location_list"),
    path("locations/<slug:code>/", views.location_detail, name="location_detail"),
    path("locations/<slug:code>/summary.json", views.location_summary, name="location_summary"),
    path("about/", views.AboutView.as_view(), name="about"),
]
