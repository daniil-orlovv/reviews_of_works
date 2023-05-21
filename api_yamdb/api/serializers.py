import re

from rest_framework import serializers

from reviews.models import User


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
