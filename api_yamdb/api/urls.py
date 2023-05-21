from django.urls import include, path
from rest_framework.routers import SimpleRouter, DefaultRouter
from api.views import SendCodeView, SendTokenView, update_user, AdminCRUDUser

router = DefaultRouter()

router.register('users', AdminCRUDUser)


urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view()),
    path('v1/auth/token/', SendTokenView.as_view()),
    path('v1/users/me/', update_user),
    path('v1/', include(router.urls))
]
