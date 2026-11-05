from django import forms
from deskhive_core.booking import InvalidBookingError, validate_booking
from .catalogue import request_spaces
from .intervals import local_interval

class BookingRequestForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Full name")
    email = forms.EmailField()
    space = forms.ChoiceField(choices=())
    start = forms.DateTimeField(widget=forms.DateTimeInput(
        format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}))
    end = forms.DateTimeField(widget=forms.DateTimeInput(
        format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["space"].choices = [("", "Choose a space")] + [
            (code, f'{space["city"]} — {space["name"]}')
            for code, space in request_spaces().items()
        ]

    def clean(self):
        data = super().clean()
        # TODO M4: guard missing fields, adapt the dates, call validate_booking,
        # translate InvalidBookingError into forms.ValidationError, return data.
        raise forms.ValidationError("M4 exercise: complete interval validation before accepting requests.")
