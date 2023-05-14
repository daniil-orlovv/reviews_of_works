from django.urls import include, path
from rest_framework.routers import SimpleRouter
from api.views import SendCodeView, SendTokenView, update_user

# router = SimpleRouter()

# router.register('v1/users/me', UpdateUser, basename='user_update')


urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view(), name='signup'),
    path('v1/auth/token/', SendTokenView.as_view(), name='login'),
    path('v1/users/me/', update_user, name='create_user'),
    #path('', include(router.urls)),
]
