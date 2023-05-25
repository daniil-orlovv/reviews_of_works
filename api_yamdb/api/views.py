from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import permission_classes
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
                             TokenRegSerializer, UserSerializer,
                             AdminCRUDSerializer)
from api.mixins import CreateListDestroyViewSet
from api_yamdb.settings import (FROM_MAIL, THEME_MAIL, TEXT_MAIL,
                                CONFIRMATION_CODE)


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
        if User.objects.filter(username=username, email=email).exists():
            send_mail(
                THEME_MAIL,
                TEXT_MAIL,
                FROM_MAIL,
                [email],
                fail_silently=False,
            )
            return Response(
                {'username': username, 'email': email},
                status=status.HTTP_200_OK
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {'Этот username занят!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {'Этот email занят!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    username=username)
                if created:
                    Code.objects.create(
                        username=username,
                        confirmation_code=CONFIRMATION_CODE)
                else:
                    code_obj, code_created = Code.objects.update_or_create(
                        username=username,
                        defaults={
                            'username': username,
                            'confirmation_code': CONFIRMATION_CODE}
                    )
                send_mail(
                    THEME_MAIL,
                    TEXT_MAIL,
                    FROM_MAIL,
                    [email],
                    fail_silently=False,
                )
                return Response(
                    {'username': username, 'email': email},
                    status=status.HTTP_200_OK
                )


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


class GetUpdateUserProfile(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', ]

    def retrieve(self, request, *args, **kwargs):
        username = request.user.username
        user = User.objects.get(username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        if 'role' in request.data:
            return Response(
                {'Вы не можете изменять поле role'},
                status=status.HTTP_400_BAD_REQUEST)
        username = request.user
        serializer = self.get_serializer(
            username,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminCRUDUser(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminCRUDSerializer
    permission_classes = [AdminPermission, permissions.IsAuthenticated]
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete', ]
