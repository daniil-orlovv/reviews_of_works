from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        role = request.user.role

        if role == 'админ':
            return True

        if role == 'модератор' and request.method in ['GET', 'POST']:
            return True
