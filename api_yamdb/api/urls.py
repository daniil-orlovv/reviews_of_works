from django.urls import include, path
from rest_framework.routers import SimpleRouter

from rest_framework.routers import DefaultRouter
from api.views import SendCodeView, SendTokenView, update_user
from api.views import (TitleViewSet, GenreViewSet,
                       CategoryViewSet, ReviewViewSet,
                       CommentViewSet)
from api.views import SendCodeView, SendTokenView, update_user, AdminCRUDUser

router = SimpleRouter()
router_v1 = DefaultRouter()

router.register('users', AdminCRUDUser)
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view()),
    path('v1/auth/token/', SendTokenView.as_view()),
    path('v1/users/me/', update_user),
    path('v1/', include(router.urls)),
    path('v1/', include(router_v1.urls))
]

