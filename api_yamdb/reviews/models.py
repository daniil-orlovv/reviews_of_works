import datetime as dt
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


def validate_year(value):
    year = dt.date.today().year
    if value > year:
        raise ValidationError('Проверьте указанный год')
    return value


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(max_length=50, default='user')


class AuthUser(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_auth',
        on_delete=models.CASCADE
    )


class Code(models.Model):
    code = models.CharField(max_length=6, blank=True, null=True)
    user = models.ForeignKey(
        User,
        related_name='user_code',
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code', 'user'],
                                    name='code_user_unique')
        ]


class Category(models.Model):
    name = models.CharField(
        verbose_name='Категория',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Жанр',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(
        verbose_name='Название'
    )
    description = models.TextField(verbose_name='Описание', null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        blank=True, null=True,
        help_text='Выберите категорию'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
        help_text='Выберите жанр'
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст коммента', null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='comments',
        blank=True, null=True
    )
    score = models.IntegerField(
        null=True)
    pub_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.text


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, blank=True,
                              null=True, related_name='reviews')
    text = models.TextField(
        verbose_name='Текст отзыва', null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reviews',
        blank=True, null=True
    )
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    pub_date = models.DateField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_review'
            )
        ]

    def __str__(self):
        return self.text
