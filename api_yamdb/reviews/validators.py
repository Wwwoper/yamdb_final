import re

from django.core.exceptions import ValidationError


def validate_characters_username(value):
    if not re.fullmatch(r"^[\w.@+-]+\Z", value):
        raise ValidationError("Недопустимые символы в username ")
