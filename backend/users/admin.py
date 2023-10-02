from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'recipe_count',
                    'follower_count')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ('username', )
    empty_value_display = '-пусто-'

    def recipe_count(self, obj):
        return obj.recipes.count()

    def follower_count(self, obj):
        return obj.followers.count()

    recipe_count.short_description = 'Количество рецептов'
    follower_count.short_description = 'Количество подписчиков'
