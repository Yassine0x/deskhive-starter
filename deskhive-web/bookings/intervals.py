"""Explicit M4 boundary: Django aware dates -> local naive core inputs."""
from zoneinfo import ZoneInfo
from django.core.exceptions import ValidationError
from django.utils import timezone

CLASSROOM_ZONE = ZoneInfo("Europe/Paris")

def local_interval(start, end):
    start = timezone.localtime(start, CLASSROOM_ZONE)
    end = timezone.localtime(end, CLASSROOM_ZONE)
    if start.utcoffset() != end.utcoffset():
        raise ValidationError("Requests crossing a clock change are outside this classroom exercise.")
    return (timezone.make_naive(start, CLASSROOM_ZONE),
            timezone.make_naive(end, CLASSROOM_ZONE))
