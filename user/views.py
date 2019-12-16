from django.shortcuts import render

import django.contrib.auth.views
from django.contrib.auth.mixins import LoginRequiredMixin

from common.views import BaseView   

class LoginView(BaseView, django.contrib.auth.views.LoginView):

    template_name = 'user/login.html'

class DashView(LoginRequiredMixin, BaseView):

    template_name = 'user/dash.html'
