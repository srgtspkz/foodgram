"""Представления (views) приложения API."""

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия."""
        if self.action in ("list", "retrieve"):
            return (AllowAny(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=("put", "delete"),
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        """Управление аватаром пользователя."""
        user = request.user

        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=("avatar",))
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(
            user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Подписка на пользователя и отписка от него."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if request.method == "POST":
            if author == user:
                return Response(
                    {"detail": "Нельзя подписаться на самого себя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if Subscription.objects.filter(
                user=user,
                author=author,
            ).exists():
                return Response(
                    {"detail": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscription.objects.create(
                user=user,
                author=author,
            )

            serializer = SubscriptionSerializer(
                author,
                context={"request": request},
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        subscription = Subscription.objects.filter(
            user=user,
            author=author,
        )

        if not subscription.exists():
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Получение списка подписок пользователя."""
        authors = User.objects.filter(
            subscribers__user=request.user,
        )

        page = self.paginate_queryset(authors)

        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags",
        "recipe_ingredients__ingredient",
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ("list", "retrieve"):
            return RecipeSerializer

        return RecipeCreateSerializer

    def perform_create(self, serializer):
        """Сохранение рецепта с привязкой к автору."""
        serializer.save(
            author=self.request.user,
        )

    @action(
        detail=True,
        methods=("get",),
        url_path="get-link",
        permission_classes=(AllowAny,),
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()

        short_link = request.build_absolute_uri(
            reverse(
                "short-link",
                kwargs={
                    "short_code": recipe.short_code,
                },
            )
        )

        return Response(
            {
                "short-link": short_link,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Работа с корзиной покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == "POST":
            if ShoppingCart.objects.filter(
                user=user,
                recipe=recipe,
            ).exists():
                return Response(
                    {"detail": ("Рецепт уже добавлен в корзину покупок.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ShoppingCart.objects.create(
                user=user,
                recipe=recipe,
            )

            serializer = RecipeShortSerializer(
                recipe,
                context={"request": request},
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe,
        )

        if not shopping_cart.exists():
            return Response(
                {"detail": ("Рецепта нет в корзине покупок.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shopping_cart.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_carts__user=request.user,
            )
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(
                total_amount=Sum("amount"),
            )
            .order_by("ingredient__name")
        )

        lines = ["Список покупок:", ""]

        for ingredient in ingredients:
            lines.append(
                (
                    f'{ingredient["ingredient__name"]} — '
                    f'{ingredient["total_amount"]} '
                    f'{ingredient["ingredient__measurement_unit"]}'
                )
            )

        content = "\n".join(lines)

        response = HttpResponse(
            content,
            content_type="text/plain; charset=utf-8",
        )
        response["Content-Disposition"] = 'attachment; filename="shopping_cart.txt"'

        return response

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Работа с избранными рецептами."""
        recipe = get_object_or_404(
            Recipe,
            pk=pk,
        )
        user = request.user

        if request.method == "POST":
            if Favorite.objects.filter(
                user=user,
                recipe=recipe,
            ).exists():
                return Response(
                    {"detail": ("Рецепт уже добавлен в избранное.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(
                user=user,
                recipe=recipe,
            )

            serializer = RecipeShortSerializer(
                recipe,
                context={"request": request},
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe,
        )

        if not favorite.exists():
            return Response(
                {"detail": ("Рецепта нет в избранном.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


def short_link_redirect(request, short_code):
    """Перенаправление по короткой ссылке."""
    recipe = get_object_or_404(
        Recipe,
        short_code=short_code,
    )

    return redirect(f"/recipes/{recipe.id}/")
