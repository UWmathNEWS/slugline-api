from django.urls import path

from user.views import login_view, logout_view

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view)
]
