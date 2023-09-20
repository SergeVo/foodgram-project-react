from django.contrib import admin
from recipes.models import (FavoritesList, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name", "slug")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ("name", "author", "favorites_count")
    search_fields = ("name",)
    list_filter = ("name", "author", "tags")

    def favorites_count(self, obj):
        return obj.favorites.count()

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


admin.site.register(FavoritesList)
admin.site.register(ShoppingCart)
