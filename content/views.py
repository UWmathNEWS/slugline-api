from django.shortcuts import render
from django.views.generic import ListView

from common.views import BaseView
from content.models import Issue

class IssuesList(BaseView):

    template_name = 'content/issue_list.html'

    def get_issues_sorted(self):
        """Get all issues, sorted into sublists by volume number.
        """
        issues_sorted = list()
        issues = list(Issue.objects.all())
        volume = list()
        last_volume = issues[0].volume_num
        for issue in issues:
            if issue.volume_num != last_volume:
                issues_sorted.append(volume)
                volume = []
            volume.append(issue)
            last_volume = issue.volume_num
        return issues_sorted

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['issue_volumes'] = self.get_issues_sorted()       
        return ctx

