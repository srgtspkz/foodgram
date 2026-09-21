"""Конфигурация маршрутизации (URL-адресов) для проекта backend."""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
