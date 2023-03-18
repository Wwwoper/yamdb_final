import datetime as dt
import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(value):
    """Проверяем на допустимый username у пользователя."""
    if not re.fullmatch(r"[\w\@\.\+\-]+", value):
        raise serializers.ValidationError("Недопустимое имя пользователя")
    if re.fullmatch(r"\b([=mM=][=eE=])\b", value):
        raise serializers.ValidationError(
            "Использовать имя me в качестве username не допустимо"
        )


def validate_year(value):
    if value > dt.datetime.now().year:
        raise ValidationError("Значение года не может быть больше текущего")
    return value
