from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework.routers import DefaultRouter
from api.views import SendCodeView, SendTokenView, update_user
from api.views import TitleViewSet, GenreViewSet, CategoryViewSet

# router = SimpleRouter()
router_v1 = DefaultRouter()
# router.register('v1/users/me', UpdateUser, basename='user_update')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view(), name='signup'),
    path('v1/auth/token/', SendTokenView.as_view(), name='login'),
    path('v1/users/me/', update_user, name='create_user'),
    path('v1/', include(router_v1.urls)),
]
