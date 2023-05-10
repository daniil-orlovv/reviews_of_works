from urllib import response
from rest_framework import viewsets, status
from rest_framework.response import Response

from django.core.mail import send_mail
from django.views import View
from django.http import JsonResponse

import shortuuid


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
        return response({'message': message}, status=status.HTTP_200_OK)


class LogInView(viewsets.ModelViewSet):
    serializer_class = ...
