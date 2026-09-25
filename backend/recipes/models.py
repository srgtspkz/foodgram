"""Модели базы данных для приложения recipes."""

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, validate_slug
from django.db import models
from utils.constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
    SHORT_CODE_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)


def generate_short_code():
    """Генерирует уникальный короткий код."""
    return uuid.uuid4().hex[:SHORT_CODE_LENGTH]


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        verbose_name="Название",
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        validators=(validate_slug,),
    )

    class Meta:
        """Мета-настройки модели тега."""

        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        """Название тега."""
        return str(self.name)


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        verbose_name="Название",
        max_length=INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        """Мета-настройки модели ингредиента."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_measurement_unit",
            ),
        )

    def __str__(self):
        """Возвращает название ингредиента и единицу измерения."""
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=RECIPE_NAME_MAX_LENGTH,
    )
    short_code = models.CharField(
        verbose_name="Короткий код",
        max_length=SHORT_CODE_LENGTH,
        unique=True,
        default=generate_short_code,
        editable=False,
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/",
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message="Время приготовления должно быть не менее 1 минуты.",
            ),
        ),
    )
    created_at = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        """Мета-настройки модели рецепта."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created_at",)

    def __str__(self):
        """Название рецепта."""
        return str(self.name)


class RecipeIngredient(models.Model):
    """Ингредиент в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message="Количество должно быть не менее 1.",
            ),
        ),
    )

    class Meta:
        """Мета-настройки модели связи ингредиентов и рецептов."""

        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецепта"
        ordering = ("recipe", "ingredient")
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            ),
        )

    def __str__(self):
        """Ингредиент, количество и единица."""
        return (
            f"{self.ingredient.name} — "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
    )

    class Meta:
        """Мета-настройки модели избранного."""

        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_favorite",
            ),
        )

    def __str__(self):
        """Возвращает строку с именем пользователя и названием рецепта."""
        return f"{self.user} — {self.recipe}"


class ShoppingCart(models.Model):
    """Модель корзины покупок."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
        verbose_name="Рецепт",
    )

    class Meta:
        """Мета-настройки модели корзины покупок."""

        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_shopping_cart",
            ),
        )

    def __str__(self):
        """Пользователь и рецепт."""
        return f"{self.user} — {self.recipe}"
