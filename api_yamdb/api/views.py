from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView

from django.core.mail import send_mail

import shortuuid

from reviews.models import User, Code


class SendCodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = self.request.data.get('email')
        username = self.request.data.get('username')
        confirmation_code = shortuuid.uuid()[:6]
        user_obj, user_created = User.objects.update_or_create(
            username=username,
            defaults={'username': username, 'email': email}
        )
        code_obj, code_created = Code.objects.update_or_create(
            user_id=user_obj.id,
            defaults={'user_id': user_obj.id, 'code': confirmation_code}
        )
        send_mail(
            'Confirmation Code',
            f'Your confirmation code: {confirmation_code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        message = f'Confirmation code sent to {email}'
        return Response({'message': message}, status=status.HTTP_200_OK)


class SendTokenView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        confirmation_code = request.data.get('confirmation_code')
        username = request.data.get('username')
        code = Code.objects.filter(code=confirmation_code).first()
        user = User.objects.filter(username=username).first()
        if code and user:
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid confirmation code or username'},
                status=status.HTTP_400_BAD_REQUEST
            )
