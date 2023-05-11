from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from django.core.mail import send_mail

import shortuuid

from reviews.models import User, Code, Token


class SendCodeView(viewsets.ModelViewSet):
    serializer_class = ...

    def perform_create(self, serializer):
        email = self.request.data.get('email')
        username = self.request.data.get('username')
        confirmation_code = shortuuid.uuid()[:6]
        Code.objects.create(code=confirmation_code)
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
        user = get_object_or_404(User, email=email)
        code = Code.objects.filter(code=confirmation_code).exists()

        if code:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            Token.objects.update_or_create(user=user, defaults={'key': token})
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid confirmation code'}, status=status.HTTP_400_BAD_REQUEST)
