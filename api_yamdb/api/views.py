import shortuuid

from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import GenreFilter
from api.permissions import IsAdmin, IsUser, ReadOnly, AdminPermission
from reviews.models import Category, Code, Comment, Genre, Review, Title, User
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleGetSerializer, TitlePostSerializer,
                             TokenRegSerializer, UserSerializer)
from api.mixins import CreateListDestroyViewSet
from api_yamdb.settings import PROJECT_EMAIL


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

    def get_queryset(self):
        return Title.objects.all().annotate(
            rating=Avg('reviews__score')
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        get_object_or_404(Title, pk=title_id)
        review_id = self.kwargs['review_id']
        get_object_or_404(Review, pk=review_id)
        return Comment.objects.filter(review=review_id)

    def perform_create(self, serializer):
        get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class SendCodeView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
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
                    PROJECT_EMAIL,
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
