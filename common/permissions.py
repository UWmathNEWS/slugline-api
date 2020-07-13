from rest_framework.permissions import BasePermission

from user.models import SluglineUser


class IsContributorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(isinstance(request.user, SluglineUser) or request.user.is_staff)


class IsCopyeditorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(
            isinstance(request.user, SluglineUser)
            and (request.user.at_least("Copyeditor") or request.user.is_staff)
        )


class IsEditorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(
            isinstance(request.user, SluglineUser)
            and (request.user.at_least("Editor") or request.user.is_staff)
        )


class IsEditor(IsEditorOrAbove):
    pass
