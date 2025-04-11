from django.contrib import admin

from apps.base.models import (Ingredient, Tag, Recipe, Subscription, Favorite,
                              ShoppingCart)


EMPTY_MSG = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = EMPTY_MSG


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value_display = EMPTY_MSG


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_author', 'text', 'cooking_time',
                    'get_tags', 'get_ingredients', 'created_at',)
    search_fields = ('name', 'author',)
    list_filter = ('tags',)
    empty_value_display = EMPTY_MSG

    @admin.display(description='Никнейм автора')
    def get_author(self, obj):
        return obj.author.username

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        tags = [tag.name for tag in obj.tags.all()]
        return ', '.join(tags)

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{ingr["ingredient__name"]} - {ingr["amount"]} '
            f'{ingr["ingredient__measurement_unit"]}.'
            for ingr in obj.recipe.values('ingredient__name', 'amount',
                                          'ingredient__measurement_unit')])


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'target', 'created_at',)
    search_fields = ('subscriber__username', 'subscriber__username',)
    empty_value_display = EMPTY_MSG


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_recipe')
    empty_value_display = EMPTY_MSG

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [f'{recipe["name"]} '
                for recipe in obj.recipe.values('name')[:7]]


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_recipe',)
    empty_value_display = EMPTY_MSG

    @admin.display(description='Рецепты')
    def get_recipe(self, obj):
        return [f'{recipe["name"]} '
                for recipe in obj.recipe.values('name')[:7]]
