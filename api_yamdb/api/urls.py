from django.urls import path
from api.views import SendCodeView, SendTokenView

urlpatterns = [
    path('v1/auth/signup/', SendCodeView.as_view(), name='signup'),
    path('v1/auth/token/', SendTokenView.as_view(), name='login'),
]
