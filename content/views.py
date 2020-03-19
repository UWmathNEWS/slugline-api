from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404
from django.db.models.functions import Length
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from content.models import Issue, Article
from content.serializers import IssueSerializer, ArticleSerializer


class IssueViewSet(ModelViewSet):

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    @action(detail=False, methods=["GET"])
    def latest(self, request):
        latest = Issue.objects.latest_issue()
        return Response(IssueSerializer(latest).data)

    @action(detail=True, methods=["GET"])
    def articles(self, request, pk=None):
        issue_articles = Article.objects.filter(issue__pk=pk)
        return Response(ArticleSerializer(issue_articles, many=True).data)


class ArticleViewSet(ModelViewSet):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
