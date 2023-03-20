from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, SingInView, SingUpView, TitleViewSet,
                    UserViewSet)

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register("titles", TitleViewSet, basename="title")
router_v1.register("genres", GenreViewSet, basename="genre")
router_v1.register("categories", CategoryViewSet, basename="category")
router_v1.register("users", UserViewSet, basename="user")
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("v1/", include(router_v1.urls)),
    path("v1/auth/token/", SingInView.as_view(), name="singin"),
    path("v1/auth/signup/", SingUpView.as_view(), name="signup"),
]
