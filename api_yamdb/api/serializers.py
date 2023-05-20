import datetime as dt
from rest_framework import serializers
from reviews.models import Title, Genre, Category, Review, User
from django.core.validators import MaxValueValidator
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from django.http import Http404

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio')
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

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'category',
                  'genre', 'year')
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

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        # Проверка, что существует title
        title_id = self.context.get('view').kwargs.get('title_id')
        try:
            get_object_or_404(Title, pk=title_id)
        except BaseException:
            raise Http404("Object not found")

        # Проверка, что пользователь не сделал больше одного отзыва
        user = self.context['request'].user

        if Review.objects.filter(author=user).count() > 0:
            raise serializers.ValidationError('You can only create one object.')

        return attrs
