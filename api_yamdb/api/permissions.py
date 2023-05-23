from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            role = request.user.role
            if role == 'admin' or request.user.is_superuser:
                return True


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and user.role not in ['user', 'moderator'])


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
                or user.role in ['moderator', 'admin'])
