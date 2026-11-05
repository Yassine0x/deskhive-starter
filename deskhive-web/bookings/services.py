"""M5 lab 2: transactional CRUD boundary. No writes before completing the lab."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from spaces.models import Space
from .models import Booking, Member


def is_available(space, start, end, exclude=None):
    # TODO M5 lab 2: half-open overlap query, excluding the optional booking pk.
    raise ValidationError('Complete M5 lab 2: is_available().')


@transaction.atomic
def save_booking(*, space, full_name, email, start, end, booking=None):
    # TODO M5 lab 2: acquire the SQLite write lock, get/create member,
    # populate candidate, full_clean, save and return it in this transaction.
    raise ValidationError('Complete M5 lab 2: save_booking().')


@transaction.atomic
def delete_booking(booking):
    # TODO M5 lab 2: delete the booking passed by the session-scoped view.
    raise ValidationError('Complete M5 lab 2: delete_booking().')
