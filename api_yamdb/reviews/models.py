from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(max_length=50, default='user')


class Category(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    slug = models.SlugField(max_length=50, blank=False, null=False)


class Genre(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    slug = models.SlugField(max_length=200, blank=False, null=False)


class Title(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)
    year = models.DateField(auto_now_add=True)
    genre = models.ForeignKey(
        Genre,
        related_name='title_genre',
        on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        related_name='title_category',
        on_delete=models.CASCADE)


class Comment(models.Model):
    ...


class Review(models.Model):
    ...

