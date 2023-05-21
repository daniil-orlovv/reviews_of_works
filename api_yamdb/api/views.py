from django.shortcuts import get_object_or_404
import shortuuid

from rest_framework import status, permissions, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import send_mail
from django.db import transaction, IntegrityError

from reviews.models import User, Code
from api.serializers import UserSerializer, TokenRegSerializer
from api.permissions import AdminPermission


class SendCodeView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = self.request.data.get('email')
            username = self.request.data.get('username')
            confirmation_code = shortuuid.uuid()[:6]

            try:
                with transaction.atomic():
                    user, created = User.objects.get_or_create(
                        email=email,
                        username=username)

                    if created:
                        Code.objects.create(
                            username=username,
                            confirmation_code=confirmation_code)
                    else:
                        code_obj, code_created = Code.objects.update_or_create(
                            username=username,
                            defaults={
                                'username': username,
                                'confirmation_code': confirmation_code}
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
                return Response(
                    error_message,
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


@permission_classes([permissions.AllowAny])
class SendTokenView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TokenRegSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        username = serializer.validated_data.get('username')
        code = Code.objects.filter(
            confirmation_code=confirmation_code).exists()
        user = get_object_or_404(User, username=username)
        if not code:
            return Response({
                'error': 'Введен неверный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user:
            return Response({
                'error': 'Такого пользователя не существует!'},
                status=status.HTTP_404_NOT_FOUND
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user(request):
    user = get_object_or_404(User, pk=request.user.id)
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
    permission_classes = [AdminPermission, permissions.IsAuthenticated]
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            error_message = {'error': 'Этот username или email заняты.'}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
