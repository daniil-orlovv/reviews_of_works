from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from django.core.mail import send_mail

import shortuuid

from reviews.models import User, Code


class SendCodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = self.request.data.get('email')
        username = self.request.data.get('username')
        confirmation_code = shortuuid.uuid()[:6]
        user = User.objects.create(username=username, email=email)
        Code.objects.create(user=user, code=confirmation_code)
        send_mail(
            'Confirmation Code',
            f'Your confirmation code: {confirmation_code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        message = f'Confirmation code sent to {email}'
        return Response({'message': message}, status=status.HTTP_200_OK)


class SendTokenView(APIView):
    def post(self, request):
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
            return Response({'error': 'Invalid confirmation code'})
