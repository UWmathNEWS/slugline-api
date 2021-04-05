import re
from user.groups import COPYEDITOR_GROUP

from django.db.models import Q
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from common.filters import SearchableFilterBackend
from common.pagination import SluglinePagination

from content.models import Issue, Article
from content.serializers import (
    IssueSerializer,
    ArticleSerializer,
    ArticleContentSerializer,
)
from content.permissions import (
    IsPublishedOrIsAuthenticated,
    IsEditorOrIsAuthenticatedReadOnly,
)
from user.models import SluglineUser


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
    search_transformers = {"__term": transform_issue_name}

    __articles_filter = SearchableFilterBackend(["title", "content_raw"])

    permission_classes = [IsEditorOrIsAuthenticatedReadOnly]

    @action(detail=False, methods=["GET"])
    def latest(self, request):
        latest = Issue.objects.latest_issue()
        return Response(IssueSerializer(latest, context={"request": request}).data)

    @action(detail=True, methods=["GET"], permission_classes=[])
    def articles(self, request, pk=None):
        """This method returns the articles associated with an issue. If the issue is not yet published and the
        requesting user is not signed in, then an error is raised.
        """
        issue = self.get_object()
        if not issue.published and not request.user.is_authenticated:
            raise NotAuthenticated()
        issue_articles = Article.objects.filter(issue__pk=pk)
        issue_articles = self.__articles_filter.filter_queryset(
            request, issue_articles, None
        )
        paginator = SluglinePagination()
        page = paginator.paginate_queryset(issue_articles, request)
        serialized = ArticleSerializer(
            page, many=True, context={"request": request}
        ).data
        return paginator.get_paginated_response(serialized)


class PublishedIssueViewSet(ReadOnlyModelViewSet):
    queryset = Issue.objects.filter(publish_date__isnull=False)
    serializer_class = IssueSerializer
    filter_backends = [SearchableFilterBackend]
    search_fields = []
    search_transformers = {"__term": transform_issue_name}

    __articles_filter = SearchableFilterBackend(["title", "content_raw"])

    @action(detail=False, methods=["GET"])
    def latest(self, request):
        latest = self.get_queryset().first()
        return Response(IssueSerializer(latest, context={"request": request}).data)


class ArticleViewSet(ModelViewSet):
    class ArticlePermissions(IsPublishedOrIsAuthenticated):
        def has_object_permission(self, request, view, article):
            if request.method in SAFE_METHODS:
                return super().has_object_permission(request, view, article)
            else:
                return isinstance(request.user, SluglineUser) and (
                    article.user == request.user
                    or request.user.at_least(COPYEDITOR_GROUP)
                )

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermissions]
    filter_backends = [SearchableFilterBackend]
    search_fields = ["title", "content_raw"]
    search_transformers = {"is": "status"}

    def list(self, request, *args, **kwargs):
        # We want to disable list view for non-authenticated users
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, author=self.request.user.writer_name)


class UserArticleViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchableFilterBackend]
    search_fields = ["title", "content_raw"]
    search_transformers = {"is": "status"}

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)


class ArticleContentViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer
    permission_classes = [IsPublishedOrIsAuthenticated]


class ArticleHTMLViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleContentSerializer
    permission_classes = [IsPublishedOrIsAuthenticated]
