from rest_framework.permissions import BasePermission

class IsFacultyOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'faculty'