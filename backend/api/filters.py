"""Фильтры приложения API."""

from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтр для поиска ингредиентов по названию."""

    name = filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        """Мета-настройки фильтра ингредиентов."""

        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    """Фильтр для поиска рецептов по тегам, автору и статусам."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    author = filters.NumberFilter(
        field_name="author__id",
    )
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )

    class Meta:
        """Мета-настройки фильтра рецептов."""

        model = Recipe
        fields = (
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранному."""
        user = self.request.user

        if value and user.is_authenticated:
            return queryset.filter(
                favorited_by__user=user,
            )

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по списку покупок."""
        user = self.request.user

        if value and user.is_authenticated:
            return queryset.filter(
                in_shopping_carts__user=user,
            )

        return queryset
