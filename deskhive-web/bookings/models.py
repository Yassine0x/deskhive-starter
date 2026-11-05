from django.core.exceptions import ValidationError
from django.db import models
from deskhive_core.booking import InvalidBookingError, validate_booking
from spaces.models import Space, TimestampedModel
from .intervals import local_interval

class Member(TimestampedModel):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.full_name

class Booking(TimestampedModel):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='bookings')
    space = models.ForeignKey(Space, on_delete=models.PROTECT, related_name='bookings')
    start = models.DateTimeField()
    end = models.DateTimeField()
    class Meta:
        ordering = ['start', 'pk']
        constraints = [models.CheckConstraint(condition=models.Q(end__gt=models.F('start')), name='booking_end_after_start')]
    def clean(self):
        # TODO M5 lab 1: validate local duration and reject overlapping bookings.
        # Exclude self.pk so updating an unchanged booking remains valid.
        raise ValidationError('Complete M5 lab 1: Booking.clean().')
