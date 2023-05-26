import re

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True, max_length=150)
    email = serializers.EmailField(
        required=True, max_length=254)
    first_name = serializers.CharField(
        required=False, max_length=150)
    last_name = serializers.CharField(
        required=False, max_length=150)

    def validate_username(self, value):
        if not re.match(r'^[\w.@+\-]*$', value):
            raise serializers.ValidationError(
                'Используйте буквы, цифры и символы @/./+/-/_')
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Поле username не может принимать значение "me"!')
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


class AdminCRUDSerializer(UserSerializer):

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Этот email занят!')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Этот username занят!')
        if not re.match(r'^[\w.@+\-]*$', value):
            raise serializers.ValidationError(
                'Используйте буквы, цифры и символы @/./+/-/_')
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ['id']
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ['id']
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    description = serializers.CharField(required=False)
    rating = serializers.IntegerField(read_only=True)

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

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'category',
                  'genre', 'year')

    def validate_year(self, value):
        year = timezone.now().date().year
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

    class Meta:
        fields = ('username', 'confirmation_code')
