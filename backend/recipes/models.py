from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    '''Модель тега.'''
    name = models.CharField(max_length=200, verbose_name="Название")
    color = models.CharField(max_length=7, verbose_name="Цвет")
    slug = models.SlugField(max_length=200, verbose_name="Слаг", unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель ингредиента.'''
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента")
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения")

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель рецепта.'''
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты")
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта")
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="images/")
    text = models.TextField(
        verbose_name="Описание")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Минимальное время - 1 минута")])
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    '''Модель связи рецепта и ингредиента.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт")
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ингредиент")
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Количество ингредиентов"
        verbose_name_plural = "Количество ингредиентов"


class FavoritesList(models.Model):
    '''Модель избранных рецептов.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites_user",
        verbose_name="Пользователь")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт")

    class Meta:
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favourites")
        ]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} добавил {self.recipe} в избранное"


class ShoppingCart(models.Model):
    '''Модель корзины покупок.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Пользователь")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепты"
        )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_cart")
        ]
