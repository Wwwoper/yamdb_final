from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name="genre", lookup_expr="slug")
    category = filters.CharFilter(field_name="category", lookup_expr="slug")
    year = filters.NumberFilter(field_name="year")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Title
        fields = ["id", "genre", "category", "year", "name"]
