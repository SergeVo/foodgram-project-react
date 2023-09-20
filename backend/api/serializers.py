from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import (FavoritesList, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "username",
                  "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Follow.objects.filter(user=request.user,
                                         author=obj).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователей."""

    class Meta(UserCreateSerializer.Meta):
        fields = ("id", "email", "username",
                  "first_name", "last_name", "password")


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, instance):
        return RecipeIngredientSerializer(
            instance.ingredients.all(),
            many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return FavoritesList.objects.filter(
            recipe=obj,
            user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if not user or user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True)
    ingredients = RecipeIngredientSerializer(many=True, required=True)
    name = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "name",
            "image",
            "cooking_time",
            "author"
        )

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Выберите тег!")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Повтор тега!")
        return value

    def add_ingredients_to_recipe(self, ingredients, recipe):
        all_ingredients = []

        for ingredient in ingredients:
            if "id" in ingredient:
                ingredient_id = ingredient["id"]
                amount = ingredient["amount"]
                try:
                    ingredient_obj = Ingredient.objects.get(id=ingredient_id)
                    all_ingredients.append(RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient_obj,
                        amount=amount))
                except Ingredient.DoesNotExist:
                    pass
            else:
                pass
        return RecipeIngredient.objects.bulk_create(all_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        print(tags)
        ingredients = validated_data.pop("ingredients")
        print(ingredients)
        validated_data["author"] = self.context.get("request").user
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        print(recipe)
        self.add_ingredients_to_recipe(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipe = super().update(instance, validated_data)
        self.add_ingredients_to_recipe(ingredients, instance)
        recipe.tags.set(tags)
        return recipe


class RecipeShortSerializer(RecipeReadSerializer):
    """ Сериализатор рецептов в укороченном формате."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoritesListSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""

    class Meta:
        model = FavoritesList
        fields = ("user", "recipe")


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка корзины."""

    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "cooking_time", "image")

    def get_image(self, obj):
        request = self.context["request"]
        image_url = obj.recipe.image.url
        return request.build_absolute_uri(image_url)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализация подписок."""

    id = serializers.ReadOnlyField()
    author = CustomUserSerializer(read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            "id",
            "author",
            "is_subscribed",
            "recipes",
            "recipes_count"
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return Follow.objects.filter(author=obj.author, user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        author = obj.author
        recipes = Recipe.objects.filter(author=author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        author = obj.author
        recipes_count = Recipe.objects.filter(author=author).count()
        return recipes_count

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError("Вы уже подписаны!")
        if user == author:
            raise serializers.ValidationError("Нельзя подписаться на себя!")
        return data