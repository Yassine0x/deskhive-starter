from django import forms
from django.core.exceptions import ValidationError
from deskhive_core.booking import InvalidBookingError, validate_booking
from spaces.models import Space
from .intervals import local_interval

class AvailabilityForm(forms.Form):
    space = forms.ModelChoiceField(queryset=Space.objects.select_related('location').all(), to_field_name='code')
    start = forms.DateTimeField(widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}))
    end = forms.DateTimeField(widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}))
    def clean(self):
        data = super().clean()
        if data.get('start') and data.get('end'):
            try:
                validate_booking(*local_interval(data['start'], data['end']))
            except (InvalidBookingError, ValueError) as exc:
                raise ValidationError(str(exc)) from exc
        return data

class PersistentBookingForm(AvailabilityForm):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
