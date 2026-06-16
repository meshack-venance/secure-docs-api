from rest_framework import permissions

from accounts.models import User


class CanAccessDocument(permissions.BasePermission):
    """Allow admins/officers globally while keeping user documents private."""

    def has_permission(self, request, view):
        # List/create access starts with authentication; queryset filtering handles scope.
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Object checks run after DRF has loaded one document from the queryset.
        if request.user.role in (User.Role.ADMIN, User.Role.OFFICER):
            return True

        return obj.uploaded_by == request.user
