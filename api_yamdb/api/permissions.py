from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and user.role not in ['user', 'moderator'])


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CategoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            (user.is_authenticated and user.role not in ['user', 'moderator'])
            or request.method in SAFE_METHODS
        )


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
                or (user.is_authenticated))
