from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views import SignUpView, LogInView

router = SimpleRouter()

router.register('/api/v1/auth/signup/', SignUpView, basename='signup')
router.register('/api/v1/auth/token/', LogInView, basename='login')

urlpatterns = [
    
]
