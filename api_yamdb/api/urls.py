from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views import SignUpView, LogInView

router = SimpleRouter()

router.register('/api/v1/auth/signup/', SendCodeView, basename='send_code')
router.register('/api/v1/auth/token/', LogInView, basename='send_code')

urlpatterns = [

    # Используется для получения access token и refresh token
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    # Используется для обновления access token
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]
