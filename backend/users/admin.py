"""Настройки панели администратора для приложения users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import Subscription, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройки отображения модели пользователя в админ-панели."""

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "avatar_preview",
        "is_active",
        "is_staff",
    )
    list_display_links = ("username",)
    list_filter = ("username",)
    search_fields = ("username",)
    search_help_text = "Поиск по имени пользователя."
    ordering = ("username",)

    fieldsets = (
        (
            "Учётные данные",
            {
                "fields": (
                    "username",
                    "password",
                ),
            },
        ),
        (
            "Личная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "avatar",
                    "avatar_preview",
                ),
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Важные даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "avatar",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ("avatar_preview",)

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        """Возвращает HTML-код для отображения миниатюры аватара."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "Нет аватара"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки отображения подписок в админ-панели."""

    list_display = (
        "id",
        "user",
        "author",
    )
    list_display_links = ("user",)
    ordering = ("user",)

    autocomplete_fields = (
        "user",
        "author",
    )


admin.site.unregister(Group)
