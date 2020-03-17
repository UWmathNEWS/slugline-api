from django.urls import path
from rest_framework.routers import SimpleRouter

from user.views import *

router = SimpleRouter()
router.register('users', UserViewSet, 'users')

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('me/', retrieve_user_view),
    path('me/', update_user_view),
    *router.urls
]
