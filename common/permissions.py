from user.groups import COPYEDITOR_GROUP, EDITOR_GROUP
from rest_framework.permissions import BasePermission, SAFE_METHODS

from user.models import SluglineUser


class SluglinePermission(BasePermission):
    def __init__(self, read_perm, write_perm):
        self.read_perm = read_perm
        self.write_perm = write_perm

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return self.read_perm.has_permission(request, view)
        else:
            return self.write_perm.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return self.read_perm.has_permission(request, view, obj)
        else:
            return self.write_perm.has_permission(request, view, obj)


class IsContributorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(isinstance(request.user, SluglineUser) or request.user.is_staff)


class IsCopyeditorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(
            isinstance(request.user, SluglineUser)
            and (request.user.at_least(COPYEDITOR_GROUP) or request.user.is_staff)
        )


class IsEditorOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(
            isinstance(request.user, SluglineUser)
            and (request.user.at_least(EDITOR_GROUP) or request.user.is_staff)
        )


class IsEditor(IsEditorOrAbove):
    pass
