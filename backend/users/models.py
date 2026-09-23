"""Модели базы данных для приложения users."""

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from utils.constants import EMAIL_MAX_LENGTH, USER_FIELD_MAX_LENGTH

username_validator = UnicodeUsernameValidator()


class User(AbstractUser):
    """Модель кастомного пользователя."""

    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=USER_FIELD_MAX_LENGTH,
        unique=True,
        validators=(username_validator,),
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=USER_FIELD_MAX_LENGTH,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=USER_FIELD_MAX_LENGTH,
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "first_name",
        "last_name",
    )

    class Meta:
        """Мета-настройки модели пользователя."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        """Имя пользователя."""
        return str(self.username)
