import datetime as dt
import re

from django.core.validators import MaxValueValidator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True)
    email = serializers.EmailField(
        required=True)
    first_name = serializers.CharField(
        required=False)
    last_name = serializers.CharField(
        required=False)

    def validate_email(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Поле email не может быть более 254 символов!')
        if not value:
            raise serializers.ValidationError(
                'Поле email не может быть пустым!')
        return value

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле username не может быть пустым!')
        if len(value) > 150:
            raise serializers.ValidationError(
                'Поле username не может быть более 150 символов!')
        if not re.match(r'^[\w.@+\-]*$', value):
            raise serializers.ValidationError(
                'Используйте буквы, цифры и символы @/./+/-/_')
        if value == 'me':
            raise serializers.ValidationError(
                'Поле username не может принимать значение "me"!')
        return value

    def validate_first_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Поле first_name не может быть более 150 символов!')
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Поле last_name не может быть более 150 символов!')
        return value

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')
        model = User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    description = serializers.CharField(required=False)
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        rate = obj.reviews.aggregate(rating=Avg('score'))
        if not rate['rating']:
            return None
        return int(rate['rating'])

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'category',
                  'genre', 'year', 'rating')
        read_only_fields = ('__all__',)


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    year = serializers.IntegerField(
        validators=[MaxValueValidator(dt.date.today().year)]
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'category',
                  'genre', 'year')

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте указанный год')
        return value

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Название не может быть больше 256 символов')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        required=True
    )
    score = serializers.IntegerField(
        required=True
    )
    pub_date = serializers.DateField(
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user
        if (self.context['request'].method == 'POST'
                and Review.objects.filter(
                title=title, author=author).exists()):
            raise serializers.ValidationError(
                'You cant create one more review')
        return attrs

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError('Score must be between 1 and 10')
        return score

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        required=True
    )
    pub_date = serializers.DateField(
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('__all__')


class TokenRegSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate_user(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле username не может быть пустым!')
        return value

    class Meta:
        fields = ('username', 'confirmation_code')
