from rest_framework import permissions

from user.models import SluglineUser
from user.groups import EDITOR_GROUP, CONTRIBUTOR_GROUP, COPYEDITOR_GROUP


class IsPublishedOrIsAuthenticated(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        return article.published or request.user.is_authenticated


class IsArticleOwnerOrReadOnly(IsPublishedOrIsAuthenticated):
    def has_object_permission(self, request, view, article):
        if request.method in permissions.SAFE_METHODS:
            return super().has_object_permission(request, view, article)
        else:
            return article.user == request.user


class IsCopyeditorOrAboveOrReadOnly(IsPublishedOrIsAuthenticated):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return isinstance(request.user, SluglineUser) and request.user.at_least(
                COPYEDITOR_GROUP
            )


class IsEditorOrReadOnly(IsPublishedOrIsAuthenticated):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return isinstance(request.user, SluglineUser) and request.user.at_least(
                EDITOR_GROUP
            )


class IsEditorOrIsAuthenticatedReadOnly(IsPublishedOrIsAuthenticated):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return isinstance(request.user, SluglineUser) and request.user.at_least(
                EDITOR_GROUP
            )
