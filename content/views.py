from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404
from django.db.models.functions import Length
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import BaseView
from content.models import Issue, Article
from content.serializers import IssueSerializer, ArticleSerializer


class IssueViewSet(ModelViewSet):

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    @action(detail=False, methods=['GET'])
    def latest(self, request):
        latest = Issue.objects.latest_issue()
        return Response(IssueSerializer(latest).data)

    @action(detail=True, methods=['GET'])
    def articles(self, request, pk=None):
        issue_articles = Article.objects.filter(issue__pk=pk)
        return Response(ArticleSerializer(issue_articles, many=True).data)

class ArticleViewSet(ModelViewSet):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


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
        featured_articles = self.get_featured_articles(ctx['issue'])
        featured_ids = [a.id for a in featured_articles]
        articles = ctx['issue'].article_set.exclude(id__in=featured_ids)
        ctx['featured_articles'] = featured_articles
        ctx['articles'] = articles
        return ctx

class ArticleView(BaseView):

    template_name = 'content/article.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Technically there is a slug parameter, but we don't use it
        ctx['article'] = Article.objects.get(id=kwargs['id'])
        return ctx

class ArticleEditView(BaseView):

    template_name = 'content/article_edit.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['article'] = Article.objects.get(id=kwargs['id'])
        return ctx
