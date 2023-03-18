from api.validators import validate_username, validate_year
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_characters_username


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name="Жанр")
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name="Категория")
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name="Произведение")
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name="Год издания"
    )
    description = models.TextField(verbose_name="Описание")
    genre = models.ManyToManyField(Genre, related_name="titles")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name="categories"
    )


class User(AbstractUser):
    class UserRole(models.TextChoices):
        ADMIN = "admin", "Админ"
        MODERATOR = "moderator", "Модератор"
        USER = "user", "Пользователь"

    role = models.CharField(
        "Пользовательская роль",
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.USER,
    )
    username = models.CharField(
        max_length=150,
        validators=[validate_characters_username, validate_username],
        unique=True,
        verbose_name="Никнейм",
    )
    email = models.EmailField(verbose_name="эл. почта", unique=True)
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        blank=True,
    )
    bio = models.TextField(verbose_name="Биография", blank=True, null=True)

    confirmation_code = models.CharField(
        "Код подтверждения", max_length=100, blank=True, null=True
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return any([self.is_superuser,
                    self.is_staff,
                    self.role == self.UserRole.ADMIN])

    @property
    def is_moderator(self):
        return self.role == self.UserRole.MODERATOR


class ParentingModel(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Review(ParentingModel):
    """Отзывы."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name="reviews")
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Отзывы"
        unique_together = (
            "author",
            "title",
        )


class Comment(ParentingModel):
    """Комментарии."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Комментарии"
        ordering = [
            "id",
        ]
