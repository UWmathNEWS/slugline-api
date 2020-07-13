from django.urls import path
from rest_framework.routers import SimpleRouter

from user.views import *

router = SimpleRouter()
router.register("users", UserViewSet, "users")

urlpatterns = [
    path("login/", login_view),
    path("logout/", logout_view),
    path("me/", current_user_view),
    path("reset_password/", reset_password_view),
    *router.urls,
]
