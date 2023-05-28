from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from api.views import (CRUDUser, CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, SendCodeView,
                       SendTokenView, TitleViewSet)

router = SimpleRouter()
router_v1 = DefaultRouter()

router_v1.register('users', CRUDUser, basename='admin_crud')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view(), name='send_confcode'),
    path('v1/auth/token/', SendTokenView.as_view(), name='send_token'),
    path('v1/', include(router_v1.urls))
]
