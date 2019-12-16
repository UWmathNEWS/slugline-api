from django.shortcuts import render

import django.contrib.auth.views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from common.views import BaseView   

class LoginView(BaseView, django.contrib.auth.views.LoginView):

    template_name = 'user/login.html'

class DashView(LoginRequiredMixin, BaseView):

    ARTICLES_PER_PAGE = 10

    template_name = 'user/dash.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        paginator = Paginator(self.request.user.article_set.all(), self.ARTICLES_PER_PAGE)
        page_num = self.request.GET.get('page', 1)
        ctx['articles'] = paginator.get_page(page_num)
        return ctx
