from rest_framework import serializers
from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'bio')
        model = User
