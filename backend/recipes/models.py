from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User
from utils.constants import (MAX_COOKING_TIME, MAX_INGREDIENT_AMOUNT,
                             MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT,
                             NAME_MAX_LENGHT, TAGS_MAX_LENGHT)


class Ingredient(models.Model):
    """ Ингридиент. """
    name = models.CharField(
        max_length=NAME_MAX_LENGHT,
        verbose_name='Название ингридиента',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=NAME_MAX_LENGHT,
        verbose_name='Еденицы измерения'
    )

    class Meta():
        ordering = ('-id', )
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингридиенты'
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
        max_length=TAGS_MAX_LENGHT,
        db_index=True,
        unique=True
    )
    color = ColorField(
        verbose_name='HEX',
        default='#1045c9',
        format='hex',
        max_length=TAGS_MAX_LENGHT,
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.slug} - {self.name}'


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
        max_length=NAME_MAX_LENGHT,
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientRecipe',
        related_name='ingredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME, message='Время приготовления \
                    не менее 1 минуты!'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME, message='Время приготовления \
                    не более 72 часов!'
            )
        ]
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
        return f'{self.name} - {self.author}'


class FavoriteReceipeShoppingCart(models.Model):
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
        ordering = ('-id', )
        verbose_name = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(FavoriteReceipeShoppingCart):
    """ Модель добавление в избраное. """

    class Meta(FavoriteReceipeShoppingCart.Meta):
        ordering = ('-id', )
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteReceipeShoppingCart):
    """ Модель списка покупок. """

    class Meta(FavoriteReceipeShoppingCart.Meta):
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
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT,
                              message='Количествоне может быть меньше 1'),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT,
                              message='Количество  не может быть больше 1000')
        ],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit} - '
            f'{self.amount}'
        )
