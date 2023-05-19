import shortuuid
import re

from rest_framework import status, permissions, viewsets, filters, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import send_mail
from django.db import transaction, IntegrityError

from reviews.models import User, Code
from api.serializers import UserSerializer
from api.permissions import AdminPermission


class SendCodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def validate_errors(username, email):
        if not email or not username:
            return {'Поле email и username не могут быть пустыми!'}
        if len(email) > 254:
            return {'Длина поля email не может превышать 254 символа!'}
        if len(username) > 150:
            return {'Длина поля username не может превышать 150 символов!'}
        if username == 'me':
            return {'Поле username не может принимать значение "me"!'}
        if not re.match(r'^[\w.@+\-]*$', username):
            return {'Используйте буквы, цифры и символы @/./+/-/_'}

    def post(self, request):
        email = self.request.data.get('email')
        username = self.request.data.get('username')
        validation_errors = self.validate_errors(username, email)
        if validation_errors:
            return Response(
                validation_errors,
                status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = shortuuid.uuid()[:6]

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    username=username)

                if created:
                    Code.objects.create(
                        user_id=user.id,
                        code=confirmation_code)
                else:
                    code_obj, code_created = Code.objects.update_or_create(
                        user_id=user.id,
                        defaults={
                            'user_id': user.id,
                            'code': confirmation_code}
                    )

                send_mail(
                    'Confirmation Code',
                    f'Your confirmation code: {confirmation_code}',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )

                return Response(
                    {'username': username, 'email': email},
                    status=status.HTTP_200_OK
                )

        except IntegrityError:
            error_message = {
                'error':
                'Пользователь с таким username или email уже существует.'}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


class SendTokenView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        confirmation_code = request.data.get('confirmation_code')
        username = request.data.get('username')
        code = Code.objects.filter(code=confirmation_code).first()
        user = User.objects.filter(username=username).first()
        if not code:
            return Response({
                'error': 'Введен неверный код подтверждения!'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not user:
            return Response({
                'error': 'Такого пользователя не существует!'},
                status=status.HTTP_404_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user(request):
    user = User.objects.get(pk=request.user.id)
    if request.method == 'PATCH':
        if 'role' in request.data:
            return Response(
                {'Вы не можете изменять поле role'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(pk=request.user.id)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCRUDUser(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminPermission, ]
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def perform_create(self, serializer):
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if User.objects.filter(email=email).exists():
            error_message = {'email': 'Этот email уже используется.'}
            raise serializers.ValidationError(error_message)
        if User.objects.filter(username=username).exists():
            error_message = {'username': 'Этот username уже используется.'}
            raise serializers.ValidationError(error_message)
        serializer.save()

    def delete(self, request, username):
        user = User.objects.get(username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)

        role = request.data.get('role')
        if role and role not in ['user', 'moderator', 'admin']:
            return Response(
                {'error': 'Недопустимая роль'},
                status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        return Response(serializer.data)
