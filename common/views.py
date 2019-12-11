from django.shortcuts import render
from django.views.generic import TemplateView

from content.models import Issue

class BaseView(TemplateView):

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['latest_issue'] = Issue.objects.latest_issue()
        return ctx

class HomeView(BaseView):

    template_name = 'common/home.html'


def page_not_found(request, exception):
    response = render(request, 'not_found.html', 
        context={ 'latest_issue': Issue.objects.latest_issue()})
    response.status_code = 404
    return response
