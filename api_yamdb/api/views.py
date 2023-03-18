from django.db.models import Avg
from django.shortcuts import get_object_or_404
# from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (AdminPermission, IsAdminOrReadOnly, IsAuthor,
                          IsModerator)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SingInSerializer,
                          SingUpSerializer, TitleCreateSerializer,
                          TitleSerializer, UserSerializer)
from .utils import send_user_confirmation_code


class SingUpView(APIView):
    """Регистрация нового пользователя с получением токена или
    получение токена для созданного администратором."""

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        user, _ = User.objects.get_or_create(username=username, email=email)
        send_user_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SingInView(APIView):
    """Авторизация пользователя на основе почты и кода подтверждения."""

    def post(self, request):
        serializer = SingInSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get("username")
            confirmation_code = serializer.data.get("confirmation_code")
            user = get_object_or_404(User, username=username)
            if user.confirmation_code != confirmation_code:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"token": str(AccessToken.for_user(user))},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    """Получение и изменение данных профиля учетной записи."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AdminPermission,)
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"

    @action(
        methods=["GET", "PATCH"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == "PATCH":
            serializer = UserSerializer(request.user,
                                        data=request.data,
                                        partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenreViewSet(CreateModelMixin,
                   DestroyModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    """Вьюсет для жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(CreateModelMixin,
                      DestroyModelMixin,
                      ListModelMixin,
                      GenericViewSet):
    """Вьюсет для категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(ModelViewSet):
    """Вьюсет для произведения."""

    queryset = (
        Title.objects.all().annotate(
            rating=Avg("reviews__score")).order_by("name")
    )
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    filterset_fields = ("category",)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(ModelViewSet):
    """Вьюсет для отзыва."""

    permission_classes = [IsModerator | IsAuthor | AdminPermission]
    serializer_class = ReviewSerializer

    def title_query(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return Review.objects.filter(title=self.title_query().id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.title_query())


class CommentViewSet(ReviewViewSet):
    """Вьюсет для комментария."""

    serializer_class = CommentSerializer
    permission_classes = [IsModerator | IsAuthor | AdminPermission]

    def review_query(self):
        return get_object_or_404(Review, id=self.kwargs.get("review_id"))

    def get_queryset(self):
        return Comment.objects.filter(review=self.review_query().id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.review_query())
