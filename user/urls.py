from django.urls import path

from user.views import auth_view

urlpatterns = [
    path('auth/', auth_view)
]
