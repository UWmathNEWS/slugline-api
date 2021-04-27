from common.permissions import SluglinePermission


class IsArticlePublished(SluglinePermission):
    def has_object_permission(self, request, view, article):
        return article.published


class IsArticleOwner(SluglinePermission):
    def has_object_permission(self, request, view, article):
        return article.user == request.user
