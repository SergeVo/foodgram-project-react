from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.serializers import (FavoritesListSerializer, FollowSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, ShoppingCartSerializer,
                             TagSerializer)
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import FavoritesList, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """Список тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CustomUserViewSet(UserViewSet):
    """Пользователи."""

    queryset = User.objects.all()

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = self.request.user
        follow = self.paginate_queryset(Follow.objects.filter(user=user))
        serializer = FollowSerializer(
            follow, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        request.data["id"] = id
        serializer = FollowSerializer(data=request.data,
                                      context={"request": request})
        if request.method == "POST":
            if serializer.is_valid():
                serializer.save(user=user, author=author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if serializer.is_valid():
                follow = get_object_or_404(Follow, user=user, author=author)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeReadSerializer

    def get_serializer_class(self):
        if self.request.method in ["POST", "PATCH"]:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk: int = None):
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            data = {
                "user": user.id,
                "recipe": recipe.id,
            }
            serializer = FavoritesListSerializer(
                data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            try:
                favorite = FavoritesList.objects.get(user=user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except FavoritesList.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        serializer_class=ShoppingCartSerializer,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.add_to(request, pk)
        elif request.method == "DELETE":
            return self.delete_from(ShoppingCart, request, pk)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def add_to(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete_from(self, model, request, pk=None):
        instance = get_object_or_404(model, recipe_id=pk, user=request.user)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
