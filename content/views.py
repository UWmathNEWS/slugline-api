import re

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from common.mixins import SearchableFilterBackend
from content.models import Issue, Article
from content.serializers import (
    IssueSerializer,
    ArticleSerializer,
    ArticleContentSerializer,
    ArticleHTMLSerializer,
)
from content.permissions import IsArticleOwnerOrReadOnly


def transform_issue_name(term):
    matches = re.match(r"(?:v?(\d+))?(?:i([0-9A-Z]+))?", term, flags=re.I)
    volume = matches[1]
    issue = matches[2]
    if volume is not None and issue is not None:
        return Q(volume_num=volume) & Q(issue_num=issue)
    elif volume is not None:
        return Q(volume_num=volume)
    elif issue is not None:
        return Q(issue_num=issue)
    else:
        return ~Q(pk__in=[])


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    filter_backends = [SearchableFilterBackend]
    search_fields = []
    search_transformers = {
        "__term": transform_issue_name
    }

    class __PseudoArticleViewSet:
        search_fields = ["title", "content_raw"]

    __articles_filter = SearchableFilterBackend()
    __articles_viewset = __PseudoArticleViewSet()

    @action(detail=False, methods=["GET"])
    def latest(self, request):
        latest = Issue.objects.latest_issue()
        return Response(IssueSerializer(latest).data)

    @action(detail=True, methods=["GET"])
    def articles(self, request, pk=None):
        issue_articles = Article.objects.filter(issue__pk=pk)
        issue_articles = self.__articles_filter.filter_queryset(request, issue_articles, self.__articles_viewset)
        return Response(ArticleSerializer(issue_articles, many=True).data)


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsArticleOwnerOrReadOnly]
    filter_backends = [SearchableFilterBackend]
    search_fields = ["title", "content_raw"]
    search_transformers = {
        "is": "status"
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, author=self.request.user.writer_name)


class UserArticleViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchableFilterBackend]
    search_fields = ["title", "content_raw"]
    search_transformers = {
        "is": "status"
    }

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)


class ArticleContentViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer


class ArticleHTMLViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer
