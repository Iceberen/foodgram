from django_filters.rest_framework import (
    CharFilter, FilterSet, ModelMultipleChoiceFilter, NumberFilter)

from apps.recipe.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по name."""

    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     queryset=Tag.objects.all(),
                                     to_field_name='slug',)
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart',
                                       field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов, добавленных в избранное."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user_id=user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов, находящихся в корзине покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(in_shopping_cart__user_id=user.id)
        return queryset
