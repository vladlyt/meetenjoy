from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsLector(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_lector


class IsNotLector(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_lector


