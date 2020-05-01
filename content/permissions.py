from rest_framework import permissions


class IsArticleOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return article.user == request.user
