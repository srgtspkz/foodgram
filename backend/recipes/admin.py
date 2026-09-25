"""Настройки панели администратора для приложения recipes."""

from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import CSV, JSON

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели тегов в админ-панели."""

    list_display = (
        "id",
        "name",
        "slug",
    )
    list_display_links = ("name",)
    ordering = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Настройки отображения модели ингредиентов в админ-панели."""

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    list_display_links = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)
    search_help_text = "Поиск по названию ингредиента."
    ordering = ("name",)

    skip_import_confirm = True

    def get_import_formats(self):
        """Возвращает список доступных форматов для импорта."""
        return [
            CSV,
            JSON,
        ]

    def get_export_formats(self):
        """Возвращает список доступных форматов для экспорта."""
        return [
            CSV,
            JSON,
        ]


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн-отображение ингредиентов в админке рецепта."""

    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения рецептов в админ-панели."""

    list_display = (
        "id",
        "name",
        "author",
        "short_code",
        "tags_display",
        "cooking_time",
        "image_preview",
        "created_at",
    )
    list_display_links = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)
    search_help_text = "Поиск по названию рецепта."
    ordering = ("-created_at",)

    autocomplete_fields = ("author",)

    filter_horizontal = ("tags",)

    readonly_fields = (
        "short_code",
        "image_preview",
        "created_at",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "author",
                    "tags",
                ),
            },
        ),
        (
            "Описание рецепта",
            {
                "fields": (
                    "text",
                    "cooking_time",
                ),
            },
        ),
        (
            "Изображение",
            {
                "fields": (
                    "image",
                    "image_preview",
                ),
            },
        ),
        (
            "Дополнительная информация",
            {
                "fields": (
                    "short_code",
                    "created_at",
                ),
            },
        ),
    )

    inlines = (RecipeIngredientInline,)

    list_select_related = ("author",)

    def get_queryset(self, request):
        """Оптимизирует запрос к БД, заранее подтягивая связанные теги."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")

    @admin.display(description="Теги")
    def tags_display(self, obj):
        """Возвращает список тегов рецепта в виде строки."""
        return ", ".join(tag.name for tag in obj.tags.all()) or "—"

    @admin.display(description="Изображение")
    def image_preview(self, obj):
        """Возвращает HTML-код для отображения миниатюры изображения."""
        if obj.image:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url,
            )
        return "Нет изображения"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки отображения избранного в админ-панели."""

    list_display = (
        "id",
        "user",
        "recipe",
    )
    list_display_links = ("user",)

    autocomplete_fields = (
        "user",
        "recipe",
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки отображения корзины покупок в админ-панели."""

    list_display = (
        "id",
        "user",
        "recipe",
    )
    list_display_links = ("user",)

    autocomplete_fields = (
        "user",
        "recipe",
    )
