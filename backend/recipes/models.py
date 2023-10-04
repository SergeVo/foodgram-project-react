from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from rest_framework import serializers

from colorfield.fields import ColorField

from common.constants import (
    MAX_LENGTH,
    MAX_TIME,
    MAX_VALUE,
    MIN_TIME,
    MIN_VALUE
)

from users.models import User


class Ingredient(models.Model):
    """ Ингридиент. """
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название ингридиента',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Еденицы измерения'
    )

    class Meta():
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """ Теги. """
    name = models.CharField(
        verbose_name='Название тега',
        max_length=7,
        db_index=True,
        unique=True
    )
    color = ColorField(
        verbose_name='HEX',
        default='#1045c9',
        format='hex',
        max_length=7,
        unique=True,

    )
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return str(self.name)


class Recipe(models.Model):
    """ Модель рецептов. """
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH,
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_TIME,
                message=f'Время приготовления не менее {MIN_TIME} минуты!'),
            MaxValueValidator(
                MAX_TIME,
                message=f'Время приготовления не более {MAX_TIME} минуты!')]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return str(self.name)


class FavoriteShoppingCart(models.Model):
    """ Связывающая модель списка покупок и избранного. """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorite(FavoriteShoppingCart):
    """ Модель добавление в избраное. """

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):
    """ Модель списка покупок. """

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'


class IngredientRecipe(models.Model):
    """ Ингридиенты рецепта. """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message=f'Значение не менее {MIN_VALUE} !'),
            MaxValueValidator(
                MAX_VALUE,
                message=f'Значение не более {MAX_VALUE} !')]
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit}'
            f' - {self.amount} '
        )
