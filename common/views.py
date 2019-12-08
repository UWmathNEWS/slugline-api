from django.shortcuts import render
from django.views.generic import TemplateView

from content.models import Issue

class BaseView(TemplateView):

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_issue'] = Issue.objects.latest_issue()
        return ctx

class HomeView(BaseView):

    template_name = 'home.html'
