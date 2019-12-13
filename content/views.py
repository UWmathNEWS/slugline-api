from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404
from django.db.models.functions import Length


from common.views import BaseView
from content.models import Issue, Article

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

class IssueView(BaseView):

    template_name = 'content/issue.html'

    NUM_FEATURED = 3

    def get_featured_articles(self, issue):
        """Get the featured articles for this issue. This works on a priority system:
        First, the article of the issue, if we have one.
        Then, any promo articles, if we have any.
        Finally, random articles we have that aren't already chosen.
        We do this until we have NUM_FEATURED articles.
        """
        featured = list()
        article_of_issue = issue.article_set.filter(is_article_of_issue=True)
        if article_of_issue.exists():
            featured.append(article_of_issue.first())
        promo_articles = issue.article_set.filter(is_promo=True)
        if promo_articles.exists():
            featured.extend(promo_articles)
        if len(featured) >= self.NUM_FEATURED:
            return featured[:self.NUM_FEATURED]
        else:
            articles_needed = self.NUM_FEATURED - len(featured)
            feature_ids = [article.id for article in featured]
            articles = issue.article_set.exclude(id__in=feature_ids)
            featured.extend(articles[:articles_needed])
            return featured

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        volume = kwargs['volume']
        issue = kwargs['issue']
        try:
            ctx['issue'] = Issue.objects.get(volume_num=volume, issue_num=issue)
        except Issue.DoesNotExist:
            raise Http404
        ctx['featured_articles'] = self.get_featured_articles(ctx['issue'])
        return ctx

class ArticleView(BaseView):

    template_name = 'content/article.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Technically there is a slug parameter, but we don't use it
        ctx['article'] =Article.objects.get(id=kwargs['id'])
        return ctx
