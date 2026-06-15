from rest_framework import permissions

from accounts.models import User


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.OFFICER
        )


class IsDocumentOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and getattr(obj, "uploaded_by", None) == request.user
        )
