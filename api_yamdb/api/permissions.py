from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from api_yamdb.settings import ADMIN, USER, MODERATOR


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            request.user.is_authenticated
            and (user.role == ADMIN or request.user.is_superuser))


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and user.role not in (USER, MODERATOR))


class GetUpdateUserPermission(permissions.BasePermission):

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
                or user.role in (MODERATOR, ADMIN))
