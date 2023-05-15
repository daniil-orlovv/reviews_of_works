from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from reviews.models import User


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        role = user.role

        if role == 'admin' and request.method in ['GET',
                                                  'POST',
                                                  'PATCH',
                                                  'DELETE']:
            return True
        else:
            raise PermissionDenied(
                "Доступ запрещен. Только для Администратора.")
