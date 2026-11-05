"""M5 lab 2: transactional CRUD boundary. No writes before completing the lab."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from spaces.models import Space
from .models import Booking, Member


def is_available(space, start, end, exclude=None):
    conflicts = Booking.objects.filter(space=space, start__lt=end, end__gt=start)
    if exclude is not None:
        conflicts = conflicts.exclude(pk=exclude)
    return not conflicts.exists()


@transaction.atomic
def save_booking(*, space, full_name, email, start, end, booking=None):
    Space.objects.filter(pk=space.pk).update(capacity=F('capacity'))
    member, _ = Member.objects.get_or_create(
        email=email.lower(), defaults={'full_name': full_name})
    candidate = booking if booking is not None else Booking()
    candidate.space = space
    candidate.member = member
    candidate.start = start
    candidate.end = end
    candidate.full_clean()
    candidate.save()
    return candidate


@transaction.atomic
def delete_booking(booking):
    booking.delete()
