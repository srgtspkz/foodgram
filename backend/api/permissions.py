"""Права доступа (permissions) приложения API."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Изменять рецепт может только его автор."""

    def has_permission(self, request, view):
        """Проверка прав на уровне запроса."""
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверка прав на уровне объекта."""
        return request.method in SAFE_METHODS or obj.author == request.user
