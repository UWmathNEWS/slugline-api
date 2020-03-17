from rest_framework.permissions import BasePermission


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_editor or request.user.is_staff))

