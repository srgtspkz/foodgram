"""Сериализаторы приложения API."""

import base64
import binascii
import uuid

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from users.models import Subscription, User
from utils.constants import MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        """Преобразует строку base64 в файл изображения."""
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                header, encoded = data.split(";base64,")
                extension = header.split("/")[-1]

                if extension == "jpeg":
                    extension = "jpg"

                decoded_file = base64.b64decode(encoded)
            except (ValueError, TypeError, binascii.Error) as e:
                raise serializers.ValidationError(
                    "Некорректное изображение в формате Base64."
                ) from e

            file_name = f"{uuid.uuid4().hex}.{extension}"
            data = ContentFile(
                decoded_file,
                name=file_name,
            )

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета-настройки сериализатора пользователей."""

        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        """Проверяет наличие подписки текущего пользователя на автора."""
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для регистрации новых пользователей."""

    class Meta(DjoserUserCreateSerializer.Meta):
        """Мета-настройки сериализатора регистрации."""

        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с аватаром пользователя."""

    avatar = Base64ImageField(
        required=True,
        allow_null=False,
    )

    class Meta:
        """Мета-настройки сериализатора аватара."""

        model = User
        fields = ("avatar",)


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для вывода подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count",
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        """Мета-настройки сериализатора подписок."""

        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Получает список рецептов автора с учетом параметра лимита."""
        recipes = obj.recipes.all()
        request = self.context.get("request")

        if request:
            recipes_limit = request.query_params.get("recipes_limit")
            if recipes_limit and recipes_limit.isdigit():
                recipes = recipes[: int(recipes_limit)]

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""

    class Meta:
        """Мета-настройки сериализатора тегов."""

        model = Tag
        fields = (
            "id",
            "name",
            "slug",
        )
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""

    class Meta:
        """Мета-настройки сериализатора ингредиентов."""

        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.IntegerField(
        source="ingredient.id",
        read_only=True,
    )
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        """Мета-настройки сериализатора."""

        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения информации о рецепте."""

    class Meta:
        """Мета-настройки краткого сериализатора рецептов."""

        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeIngredientCreateSerializer(serializers.Serializer):
    """Сериализатор для добавления ингредиента при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
    )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = UserSerializer(
        read_only=True,
    )
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients",
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета-настройки сериализатора рецептов."""

        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном."""
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.favorited_by.filter(
            user=request.user,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в корзине покупок."""
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.in_shopping_carts.filter(
            user=request.user,
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
    )

    class Meta:
        """Мета-настройки сериализатора создания рецептов."""

        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        """Валидация входящих данных."""
        if "ingredients" not in self.initial_data:
            raise serializers.ValidationError(
                {"ingredients": ("Это поле обязательно.")}
            )

        if "tags" not in self.initial_data:
            raise serializers.ValidationError({"tags": ("Это поле обязательно.")})

        return data

    def validate_tags(self, tags):
        """Валидация списка тегов."""
        if not tags:
            raise serializers.ValidationError("Нужно указать хотя бы один тег.")

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Теги не должны повторяться.")

        return tags

    def validate_ingredients(self, ingredients):
        """Валидация списка ингредиентов."""
        if not ingredients:
            raise serializers.ValidationError("Нужно указать хотя бы один ингредиент.")

        ingredient_ids = [item["id"].id for item in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")

        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        """Массовое создание связей ингредиентов с рецептом."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item["id"],
                amount=item["amount"],
            )
            for item in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(
            **validated_data,
        )

        recipe.tags.set(tags)
        self.create_ingredients(
            recipe,
            ingredients,
        )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop(
            "ingredients",
            None,
        )

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(
                instance,
                ingredients,
            )

        return instance

    def to_representation(self, instance):
        """Определяет формат вывода данных рецепта."""
        return RecipeSerializer(
            instance,
            context=self.context,
        ).data
