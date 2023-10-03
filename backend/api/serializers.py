# pylint: disable=no-member
# from django.shortcuts import get_object_or_404
# from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.core.validators import MinValueValidator
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from common.constants import MIN_VALUE

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор пользователя """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )

    def get_is_subscribed(self):
        request = self.context.get('request')
        user = request.user if request.user.is_authenticated else None
        return request, user


# class UserCreateSerializer(serializers.ModelSerializer):
#     """ Сериализатор создания пользователя """

#     class Meta:
#         model = User
#         fields = (
#             'email', 'username', 'first_name',
#             'last_name', 'password')


class SubscribeListSerializer(UserSerializer):
    """ Сериализатор подписок """
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    # def validate(self, data):
    #     author_id = self.context.get(
    #         'request').parser_context.get('kwargs').get('id')
    #     author = get_object_or_404(User, id=author_id)
    #     user = self.context.get('request').user
    #     if user.follower.filter(author=author_id).exists():
    #         raise ValidationError(
    #             detail='Подписка уже существует',
    #             code=status.HTTP_400_BAD_REQUEST,
    #         )
    #     if user == author:
    #         raise ValidationError(
    #             detail='Нельзя подписаться на самого себя',
    #             code=status.HTTP_400_BAD_REQUEST,
    #         )
    #     return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                limit = None
            if limit:
                recipes = recipes[:limit]
        return RecipeShortSerializer(recipes, many=True, read_only=True).data


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра тегов """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра ингридиентов """
    id = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор связи ингридиентов и рецепта """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value < MIN_VALUE:
            raise serializers.ValidationError(
                'Количество должно быть больше 0')
        return value

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра рецепта """
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredienttorecipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    # def get_ingredients(self, obj):
    #     ingredients = IngredientRecipe.objects.filter(recipe=obj)
    #     return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if (
            request and request.user.is_authenticated) else None
        if not user:
            return request, user
        return request, obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if (
            request and request.user.is_authenticated) else None
        if not user:
            return request, user
        return request, obj.shopping_list.filter(user=user).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания рецепта """
    ingredients = IngredientRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        error_messages={
            'min_value': (
                f'Время приготовления не менее {MIN_VALUE} минуты!'
            )
        })

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)

    def validate_tags(self, tags):
        if len(tags) == 0:
            raise ValidationError('Необходимо выбрать хотя бы один тег')

        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise ValidationError('Теги должны быть уникальны')

        return tags

    def validate_ingredients(self, ingredients):
        ingredients_dict = {}

        if not ingredients:
            raise serializers.ValidationError('Отсутствуют ингридиенты')

        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_dict:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальны')
            ingredients_dict[ingredient_id] = ingredient

        return list(ingredients_dict.values())

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Необходимо добавить изображение')
        return image

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_liist.append(
                IngredientRecipe(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe,
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """ Сериализатор полей избранных рецептов и покупок """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteAndShoppingCartSerializer(serializers.ModelSerializer):
    """ Универсальный сериализатор для избранных рецептов и списка покупок """

    class Meta:
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        model = self.Meta.model

        if model.objects.filter(user=user, recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен.'
            )

        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(FavoriteAndShoppingCartSerializer):
    """ Сериализатор избранных рецептов """
    class Meta(FavoriteAndShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteAndShoppingCartSerializer):
    """ Сериализатор списка покупок """
    class Meta(FavoriteAndShoppingCartSerializer.Meta):
        model = ShoppingCart
