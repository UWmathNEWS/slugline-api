from rest_framework import permissions


class IsArticleOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, article):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return article.user == request.user


class IsCopyeditorOrAboveOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.at_least("Copyeditor") or request.user.is_staff


class IsEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.at_least("Editor") or request.user.is_staff
