from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.user.is_authenticated:
            role = request.user.role
            if role == 'admin' or request.user.is_superuser:
                return True
