from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "first_name",
        "last_name",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_follow")
        ]
