from django.contrib import admin
from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админпанель пользователей."""

    list_display = ("id", "username", "email", "first_name", "last_name")
    list_filter = ("username", "email")
    search_fields = ("username", "email")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админпанель подписок."""

    list_display = ("id", "user", "author")
    list_filter = ("user", "author")
    search_fields = ("user", "author")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
