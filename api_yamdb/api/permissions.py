from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            request.user.is_authenticated
            and (user.is_admin or request.user.is_superuser))


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and not user.is_user
            and not user.is_moderator)


class MePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'role' not in request.data:
            return True


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            (user.is_authenticated)
            or request.method in SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (request.method in SAFE_METHODS
                or obj.author == user
                or user.is_moderator
                or user.is_admin)
