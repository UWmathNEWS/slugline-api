from rest_framework.permissions import BasePermission

from user.models import SluglineUser


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            isinstance(request.user, SluglineUser)
            and (request.user.is_editor or request.user.is_staff)
        )
