from django.shortcuts import render
from django.views.generic import ListView
from django.http import Http404

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from content.models import Issue, Article
from content.serializers import (
    IssueSerializer,
    ArticleSerializer,
    ArticleContentSerializer,
    ArticleHTMLSerializer,
)
from content.permissions import IsArticleOwnerOrReadOnly, IsEditorOrReadOnly


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    permission_classes = [IsEditorOrReadOnly]
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

    permission_classes = [IsAuthenticatedOrReadOnly, IsArticleOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, author=self.request.user.writer_name)


class UserArticleViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)


class ArticleContentViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer


class ArticleHTMLViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer
