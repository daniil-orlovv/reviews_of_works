from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.core.validators import RegexValidator, MaxLengthValidator


from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
            ),
            MaxLengthValidator(150)
        ])
    email = serializers.EmailField(
        required=True,
        validators=[
            MaxLengthValidator(254)
        ])
    first_name = serializers.CharField(
        required=False,
        validators=[
            MaxLengthValidator(150)
        ])
    last_name = serializers.CharField(
        required=False,
        validators=[
            MaxLengthValidator(150)
        ])

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        model = User
