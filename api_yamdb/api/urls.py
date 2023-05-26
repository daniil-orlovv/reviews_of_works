from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from api.views import (AdminCRUDUser, CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, SendCodeView,
                       SendTokenView, TitleViewSet, GetUpdateUserProfile)

router = SimpleRouter()
router_v1 = DefaultRouter()

router_v1.register('users', AdminCRUDUser, basename='admin_crud')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view(), basename='send_confcode'),
    path('v1/auth/token/', SendTokenView.as_view(), basename='send_token'),
    path('v1/users/me/', GetUpdateUserProfile.as_view({
        'get': 'retrieve',
        'patch': 'partial_update'}), basename='getupdate_user'),
    path('v1/', include(router_v1.urls))
]
