from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_year(value):
    year = timezone.now().date().year
    if value > year:
        raise ValidationError('Проверьте указанный год')
    return value
