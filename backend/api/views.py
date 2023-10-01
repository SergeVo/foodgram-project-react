# pylint: disable=no-member
from django.db.models import Prefetch, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from recipes.models import (Favorite, Ingredient,
                            IngredientRecipe, Recipe, Tag)

from users.models import Follow, User

from .filters import IngredientFilter
from .pagination import CustomPagination
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscribeListSerializer,
                          TagSerializer, UserSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    ''' ViewSet для ингредиентов '''
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    ''' ViewSet для тегов '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    ''' ViewSet для рецептов '''
    queryset = Recipe.objects.select_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.all(), to_attr='tag_list'),
        Prefetch('ingredienttorecipe_set',
                 queryset=IngredientRecipe.objects.select_related
                 ('ingredient'), to_attr='ingredient_list')
    )
    serializer_class = RecipeReadSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return CreateRecipeSerializer

    @staticmethod
    def send_message(ingredients):
        ''' Формирование списка ингредиентов '''
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f'\n{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["amount"]}')
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ''' Скачивание списка ингредиентов '''
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        ingredients = sorted(ingredients, key=lambda x: x['ingredient__name'])
        return self.send_message(ingredients)

    @staticmethod
    def _add_to_list(serializer, recipe, user, request):
        context = {'request': request}
        data = {'user': user.id, 'recipe': recipe.id}
        serializer_instance = serializer(data=data, context=context)
        serializer_instance.is_valid(raise_exception=True)
        serializer_instance.save()
        return serializer_instance.data

    @action(detail=True,
            methods=('POST',),
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        ''' Добавление рецепта в список покупок '''
        recipe = get_object_or_404(Recipe, id=pk)
        serializer_data = self._add_to_list(ShoppingCartSerializer,
                                            recipe,
                                            request.user,
                                            request)
        return Response(serializer_data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=('POST',),
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        ''' Добавление рецепта в список избранных '''
        recipe = get_object_or_404(Recipe, id=pk)
        serializer_data = self._add_to_list(FavoriteSerializer,
                                            recipe,
                                            request.user,
                                            request)
        return Response(serializer_data, status=status.HTTP_201_CREATED)

    @action(mapping={'delete': 'delete'},
            detail=True, methods=('delete',),
            permission_classes=[IsAuthenticated])
    def delete_from_list(self, request, prmary_key):
        ''' Удаление рецепта из списка покупок '''
        if 'favorite' in request.path:
            serializer_class = FavoriteSerializer
        else:
            serializer_class = ShoppingCartSerializer

        queryset = serializer_class.Meta.model.objects.filter(
            user=request.user,
            recipe=prmary_key)
        if queryset.exists():
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def destroy_favorite(self, request, recipe_id):
        ''' Удаление рецепта из избранных '''
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=recipe_id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(BaseUserViewSet):
    ''' ViewSet для пользователя '''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, user_id):
        ''' Подписка на автора '''
        user = request.user
        author = get_object_or_404(User, pk=user_id)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        ''' Список подписок '''
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
