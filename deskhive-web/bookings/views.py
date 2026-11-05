from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe
from .catalogue import request_spaces
from .forms import BookingRequestForm
from .intervals import CLASSROOM_ZONE
from django.utils import timezone

SESSION_KEY = "m4_last_request"

@require_http_methods(["GET", "HEAD", "POST"])
def booking_request(request):
    form = BookingRequestForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        space = request_spaces()[data["space"]]
        # Explicit allowlist: never store arbitrary POST values or datetime objects.
        request.session[SESSION_KEY] = {
            "full_name": data["full_name"], "email": data["email"],
            "space": data["space"], "space_name": space["name"],
            "start": timezone.localtime(data["start"], CLASSROOM_ZONE).isoformat(),
            "end": timezone.localtime(data["end"], CLASSROOM_ZONE).isoformat(),
        }
        request.session.set_expiry(1800)
        return redirect("bookings:thanks")
    return render(request, "bookings/request.html", {"form": form})

@require_safe
def booking_thanks(request):
    summary = request.session.get(SESSION_KEY)
    if summary is None:
        return redirect("bookings:request")
    return render(request, "bookings/thanks.html", {"summary": summary})
