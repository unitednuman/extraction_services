from rest_framework.permissions import BasePermission
from .constants import UserTypes


class IsAppAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:

            return request.session.get('role', UserTypes.USER) == UserTypes.ADMIN
        else:
            return False


class IsNonAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return request.session.get('role', UserTypes.USER) == UserTypes.USER
        else:
            return False
