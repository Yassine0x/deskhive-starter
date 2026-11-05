from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class Location(TimestampedModel):
    code = models.CharField(max_length=3, primary_key=True)
    city = models.CharField(max_length=80)
    address = models.CharField(max_length=200)
    def __str__(self):
        return self.city

class Space(TimestampedModel):
    code = models.SlugField(max_length=30, unique=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='spaces')
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=20, choices=[('desk', 'Desk'), ('meeting_room', 'Meeting room')])
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    hourly_rate = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    class Meta:
        ordering = ['pk']
        constraints = [models.CheckConstraint(condition=models.Q(capacity__gte=1), name='space_capacity_positive'),
                       models.CheckConstraint(condition=models.Q(hourly_rate__gt=0), name='space_rate_positive')]
    def __str__(self):
        return self.name
