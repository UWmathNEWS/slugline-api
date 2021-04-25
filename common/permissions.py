from user.groups import COPYEDITOR_GROUP, EDITOR_GROUP
from rest_framework.permissions import BasePermission, SAFE_METHODS

from user.models import SluglineUser


def create_permission(read_perm, write_perm):
    """
    Creates a new permission class using read_perm
    for the readonly permission, and write_perm for the write
    permission.

    Since DRF uses permission classes and not instances of
    those classes, this function takes classes as arguments and
    creates a local class and returns it.
    """

    # we need instances to call the methods on
    read_instance = read_perm()
    write_instance = write_perm()

    class NewPermission(BasePermission):
        def has_permission(self, request, view):
            if request.method in SAFE_METHODS:
                return read_instance.has_permission(request, view)
            else:
                return write_instance.has_permission(request, view)

        def has_object_permission(self, request, view, obj):
            if request.method in SAFE_METHODS:
                return read_instance.has_object_permission(request, view, obj)
            else:
                return write_instance.has_object_permission(request, view, obj)

    return NewPermission


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
