from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view

from django.core.mail import send_mail

import shortuuid

from reviews.models import User


class SignUpView(viewsets.ModelViewSet):
    serializer_class = ...

    def perform_create(self, serializer):
        email = self.request.data.get('email')
        username = self.request.data.get('username')
        confirmation_code = shortuuid.uuid()[:6]
        send_mail(
            'Confirmation Code',
            f'Your confirmation code: {confirmation_code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        serializer.save(email=email, username=username)
        message = f'Confirmation code sent to {email}'
        return Response({'message': message}, status=status.HTTP_200_OK)


class SendTokenView(TokenObtainPairView):
    @staticmethod
    @api_view(['POST'])
    def post(request):
        confirmation_code = request.data.get('confirmation_code')
        email = request.data.get('email')

        if not confirmation_code or not email:
            return Response({'error': 'Invalid confirmation code or email'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if confirmation_code != user.confirmation_code:
            return Response({'error': 'Invalid confirmation code'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        # Сохранение токена в профиле пользователя или где-то еще, по вашему выбору
        user.token = token
        user.save()

        return Response({'token': token}, status=status.HTTP_200_OK)
