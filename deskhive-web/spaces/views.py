"""M4: templates over the existing in-memory catalogue."""
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_safe
from .data import LOCATIONS

def get_location(code):
    try:
        return LOCATIONS[code]
    except KeyError as exc:
        raise Http404("Unknown DeskHive location") from exc

@require_safe
def home(request):
    return render(request, "spaces/home.html")

@require_safe
def location_list(request):
    return render(request, "spaces/location_list.html", {"locations": LOCATIONS})

@require_safe
def location_detail(request, code):
    return render(request, "spaces/location_detail.html",
                  {"code": code, "location": get_location(code)})

@require_safe
def location_summary(request, code):
    return JsonResponse({"code": code, **get_location(code)})

class AboutView(View):
    http_method_names = ["get", "head", "options"]

    def get(self, request):
        return render(request, "spaces/about.html")
