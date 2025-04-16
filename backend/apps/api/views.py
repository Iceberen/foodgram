from io import StringIO

from apps.api.filters import IngredientFilter, RecipeFilter
from apps.api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                                  IngredientSerializer, ReadRecipeSerializer,
                                  ShoppingCartSerializer,
                                  ShortRecipeSerializer, TagSerializer)
from apps.base.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                              ShoppingCart, Tag)
from apps.base.pagination import Pagination
from apps.base.permissions import IsOwnerOrReadOnly
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

User = get_user_model()


class TagView(viewsets.ModelViewSet):
    """Представления тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'head', 'options')
    pagination_class = None


class IngredientView(viewsets.ModelViewSet):
    """Представления ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'head', 'options')
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination
    queryset = Recipe.objects.all()
    serializer_class = ReadRecipeSerializer

    def get_permissions(self):
        """Получение класса ограничения."""
        if self.action in ('list', 'retrieve', 'recipe_by_link'):
            return (AllowAny(),)
        elif self.action in ('update', 'partial_update', 'destroy',):
            return (IsOwnerOrReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        """Выбор класса сериализатора."""
        if self.action == 'favorite':
            return ShortRecipeSerializer
        elif self.action in ('update', 'partial_update', 'create', 'destroy'):
            return CreateRecipeSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['GET'], url_path='get-link')
    def recipe_by_link(self, request, pk=None):
        """Создание линка на рецепт."""
        short_link_recipe = get_object_or_404(Recipe, id=pk).short_link
        short_link = f'{settings.SITE_DOMAIN}/s/{short_link_recipe}'
        return Response({'short-link': short_link})

    @action(detail=True, methods=['POST', 'DELETE'], url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            data = {'recipe': recipe.id, 'user': user.id}
            serializer = FavoriteSerializer(data=data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        instance = Favorite.objects.filter(recipe=recipe, user=user)
        if not instance.exists():
            return Response({'error': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({'detail': 'Рецепт успешно удалён из избранного.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], url_path='shopping_cart',
            permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из корзины."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            data = {'recipe': recipe.id, 'user': user.id}
            serializer = ShoppingCartSerializer(data=data,
                                                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        instance = ShoppingCart.objects.filter(recipe=recipe, user=user)
        if not instance.exists():
            return Response({'error': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({'detail': 'Рецепт успешно удалён из корзины.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request):
        """Скачать список ингредиентов из корзины."""
        ingredients = (
            RecipeIngredient.objects.
            filter(recipe__in_shopping_cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        output = '\n'.join(
            f'{num}. {item["ingredient__name"]} - '
            f'{item["total_amount"]} '
            f'{item["ingredient__measurement_unit"]}.'
            for num, item in enumerate(ingredients, start=1)
        )
        return HttpResponse(output, content_type='text/plain')


@api_view(['GET'])
@permission_classes((AllowAny, ))
def recipe_by_link(request, short_link):
    """Получить рецепт по короткой ссылке."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    serializer = ReadRecipeSerializer(recipe, context={'request': request})
    return Response(serializer.data)
