import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from reviews.models import Category, Comment, Genre, Review, Title, User
from tqdm import tqdm


def reader(file_name: str):
    file_path = os.path.join(settings.BASE_DIR, "static/data/", file_name)
    csvfile = open(file_path, newline="")
    reader = csv.DictReader(csvfile)
    return reader


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file_reader = reader("users.csv")
        for row in tqdm(csv_file_reader, unit=" import user"):
            User.objects.get_or_create(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"],
                bio=row["bio"],
                first_name=row["first_name"],
                last_name=row["last_name"],
            )

        csv_file_reader = reader("genre.csv")
        for row in tqdm(csv_file_reader, unit=" import genre"):
            Genre.objects.get_or_create(
                id=row["id"], name=row["name"], slug=row["slug"]
            )

        csv_file_reader = reader("category.csv")
        for row in tqdm(csv_file_reader, unit=" import category"):
            Category.objects.get_or_create(
                id=row["id"], name=row["name"], slug=row["slug"]
            )

        csv_file_reader = reader("titles.csv")
        for row in tqdm(csv_file_reader, unit=" import title"):
            category = get_object_or_404(Category, id=row["category"])
            Title.objects.get_or_create(
                id=row["id"], name=row["name"],
                year=row["year"], category=category
            )

        csv_file_reader = reader("review.csv")
        for row in tqdm(csv_file_reader, unit=" import review"):
            user = get_object_or_404(User, id=row["author"])
            title = get_object_or_404(Title, id=row["title_id"])
            Review.objects.get_or_create(
                id=row["id"],
                title=title,
                text=row["text"],
                author=user,
                score=row["score"],
                pub_date=row["pub_date"],
            )

        csv_file_reader = reader("comments.csv")
        for row in tqdm(csv_file_reader, unit=" import comment"):
            user = get_object_or_404(User, id=row["author"])
            review = get_object_or_404(Review, id=row["review_id"])
            Comment.objects.get_or_create(
                id=row["id"],
                review=review,
                text=row["text"],
                author=user,
                pub_date=row["pub_date"],
            )
