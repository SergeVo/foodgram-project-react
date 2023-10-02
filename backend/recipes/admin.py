from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    ''' Количество полей для добавления ингридиентов в админке '''
    model = IngredientRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ''' Админ панель управление рецептами '''
    list_display = ('author', 'name', 'cooking_time',
                    'get_favorites', 'get_ingredients',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientInline,)

    def get_favorites(self, obj):
        ''' Вывод количества избранных рецептов '''
        return obj.favorites.count()
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        ''' Вывод списка ингридиентов '''
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])
    get_ingredients.short_description = 'Ингридиенты'


class IngredientAdmin(admin.ModelAdmin):
    """ Админ панель управление ингридиентами """
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )


class TagAdmin(admin.ModelAdmin):
    """ Админ панель управление тегами """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )


class FavoriteAdmin(admin.ModelAdmin):
    """ Админ панель управление подписками """
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    """ Админ панель списка покупок """
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = '-пусто-'


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
