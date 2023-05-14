from rest_framework import serializers
from django.core.validators import RegexValidator

from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
            )
        ])
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio')
        model = User
