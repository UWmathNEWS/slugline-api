from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404
from django.db.models.functions import Length
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from content.models import Issue, Article
from content.serializers import (
    IssueSerializer,
    ArticleSerializer,
    ArticleContentSerializer,
    ArticleHTMLSerializer,
)


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


class UserArticleViewSet(ModelViewSet):
    """A viewset that returns just the articles for the request's user."""

    serializer_class = ArticleSerializer

    @permission_classes([IsAuthenticated])
    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)


class ArticleContentViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    """A detail-only viewset that just returns the content_raw of an article."""

    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer

    @permission_classes([IsAuthenticated])
    def update(self, request, pk=None):
        try:
            article = Article.objects.get(id=pk)
            if article.user != request.user:
                raise PermissionDenied
            article.content_raw = request.data["content_raw"]
            article.save()
        except:
            raise Http404


class ArticleHTMLViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """A detail-only viewset that just returns the content_raw of an article."""

    queryset = Article.objects.all()
    serializer_class = ArticleHTMLSerializer
