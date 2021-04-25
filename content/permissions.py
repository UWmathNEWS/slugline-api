from common.permissions import SluglinePermission

from user.models import SluglineUser
from user.groups import EDITOR_GROUP, CONTRIBUTOR_GROUP, COPYEDITOR_GROUP


class IsArticlePublished(SluglinePermission):
    def has_object_permission(self, request, view, article):
        return article.published


class IsArticleOwner(SluglinePermission):
    def has_object_permission(self, request, view, article):
        return article.user == request.user
