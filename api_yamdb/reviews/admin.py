from django.contrib import admin
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")


class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")


class TitleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "year", "description", "category")


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Review)
