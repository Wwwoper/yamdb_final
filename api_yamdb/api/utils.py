from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from reviews.models import User


def send_user_confirmation_code(user) -> None:
    """Генератор кода для подтверждения регистрации пользователя.
    Создает код подтверждения и отправляет его на эл. почту
    """
    user = get_object_or_404(User, username=user.username)
    user.confirmation_code = default_token_generator.make_token(user)
    user.save()
    send_mail(
        "Код подтверждения регистрации",
        user.confirmation_code,
        settings.EMAIL_FROM,
        [user.email],
        fail_silently=False,
    )
