from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

from reviews.validators import validate_year
from api_yamdb.settings import ADMIN, USER, MODERATOR


class User(AbstractUser):
    ROLE_CHOICES = [
        (ADMIN, 'admin'),
        (USER, 'user'),
        (MODERATOR, 'moderator'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER
    )
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='username_email_unique')
        ]

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class Category(models.Model):
    name = models.CharField(
        verbose_name='Категория',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='slug',
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
        verbose_name='slug',
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
        validators=[MinValueValidator(
                    1,
                    message='Значение должно быть 1 или больше'),
                    MaxValueValidator(
                    10,
                    message='Значение должно быть не больше 10')])
    pub_date = models.DateField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_review'
            )
        ]
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=True,
                               null=True, related_name='comments')
    text = models.TextField(
        verbose_name='Текст коммента', null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='comments',
        blank=True, null=True
    )
    pub_date = models.DateField(auto_now=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
