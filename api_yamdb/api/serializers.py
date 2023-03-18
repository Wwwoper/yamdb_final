from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User

from .validators import validate_username


class SingUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True,
                                     validators=[validate_username])

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")
        used_username = User.objects.filter(username=username).exists()
        used_email = User.objects.filter(email=email).exists()
        if User.objects.filter(username=username, email=email).exists():
            return data
        if used_username or used_email:
            raise serializers.ValidationError("Имя или почта уже используются")
        return data


class SingInSerializer(serializers.ModelSerializer):
    """Сериализатор для авторизации пользователя."""

    class Meta:
        model = User
        fields = ("username", "confirmation_code")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя."""

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""

    lookup_field = "slug"

    class Meta:
        # При использовании fields = '__all__' падают тесты
        fields = (
            "name",
            "slug",
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""

    lookup_field = "slug"

    class Meta:
        fields = (
            "name",
            "slug",
        )
        model = Genre


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведения."""

    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Genre.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер для отзыва. Валидирует оценку и уникальность."""

    title = serializers.SlugRelatedField(slug_field="name",
                                         read_only=True)
    author = serializers.SlugRelatedField(slug_field="username",
                                          read_only=True)

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError("Оценка по 10-бальной шкале!")
        return value

    def validate(self, data):
        request = self.context["request"]
        author = request.user
        title_id = self.context.get("view").kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == "POST"
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError("Больше одного отзыва на title "
                                  "писать нельзя")
        return data

    class Meta:
        model = Review
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для комментария."""

    review = serializers.SlugRelatedField(slug_field="text",
                                          read_only=True)
    author = serializers.SlugRelatedField(slug_field="username",
                                          read_only=True)

    class Meta:
        fields = "__all__"
        model = Comment
