from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'recipe_count',
                    'follower_count')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ('username',)
    empty_value_display = '-пусто-'

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Количество рецептов'

    def follower_count(self, obj):
        return obj.following.count()
    follower_count.short_description = 'Количество подписчиков'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user__username', 'author__username')
    list_filter = ('user__username', 'author__username')
    ordering = ('-id',)
    empty_value_display = '-пусто-'
