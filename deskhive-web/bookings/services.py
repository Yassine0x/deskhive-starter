"""Validated writes; the SQLite write lock precedes the overlap query.

All classroom booking writes must use this service. Direct ORM save/update
bypasses validation; full_clean is not automatically called by Django save.
"""
from django.db import transaction
from django.db.models import F
from spaces.models import Space
from .models import Booking, Member

def is_available(space, start, end, exclude=None):
    return not Booking.objects.filter(space=space, start__lt=end, end__gt=start).exclude(pk=exclude).exists()

@transaction.atomic
def save_booking(*, space, full_name, email, start, end, booking=None):
    # A write before reading serializes classroom SQLite writers. On a busy
    # database the caller reports a retry, rather than silently saving a clash.
    Space.objects.filter(pk=space.pk).update(capacity=F('capacity'))
    member, _ = Member.objects.get_or_create(email=email.lower(), defaults={'full_name': full_name})
    candidate = booking or Booking()
    candidate.space, candidate.member = space, member
    candidate.start, candidate.end = start, end
    candidate.full_clean()
    candidate.save()
    return candidate

@transaction.atomic
def delete_booking(booking):
    booking.delete()
