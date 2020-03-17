from django.urls import path
from rest_framework.routers import SimpleRouter

from user.views import *

router = SimpleRouter()
router.register('users', UserViewSet, 'users')

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('auth/', auth_view),
    path('user/', retrieve_user_view),
    path('user/', update_user_view),
    *router.urls
]
