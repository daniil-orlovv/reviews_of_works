import shortuuid

from rest_framework import status, permissions, viewsets, filters, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from django.core.mail import send_mail

from reviews.models import User, Code, Category, Genre, Title, Review
from api.serializers import (UserSerializer, CategorySerializer,
                             GenreSerializer, TitleGetSerializer,
                             TitlePostSerializer, ReviewSerializer)
from .permissions import IsAdmin, ReadOnly, ReviewPermission
from .filters import GenreFilter


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = [IsAdmin | ReadOnly]
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdmin | ReadOnly]


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    ordering_fields = ('year', 'name')
    permission_classes = [IsAdmin | ReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = GenreFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleGetSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        get_object_or_404(Title, pk=title_id)
        return Review.objects.filter(title=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


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


@api_view(['GET', 'PATCH'])
def update_user(request):
    user = User.objects.get(pk=request.user.id)
    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(pk=request.user.id)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)
