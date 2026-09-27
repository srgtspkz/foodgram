"""Классы пагинации приложения API."""

from rest_framework.pagination import PageNumberPagination
from utils.constants import PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    """Кастомный класс пагинации для проекта Foodgram."""

    page_size = PAGE_SIZE
    page_size_query_param = "limit"
