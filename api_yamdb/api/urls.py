from rest_framework.routers import SimpleRouter
from api.views import SendCodeView, SendTokenView

router = SimpleRouter()

router.register('/api/v1/auth/signup/', SendCodeView, basename='signup')
router.register('/api/v1/auth/token/', SendTokenView, basename='login')

urlpatterns = [

]
