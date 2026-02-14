"""
Custom permissions.
Admin portal endpoints require staff/superuser access.
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Only allow staff users (admin portal access)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsAdminOrReadOnly(BasePermission):
    """Allow read for anyone, write only for admin."""

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
