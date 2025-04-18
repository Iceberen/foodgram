from django.contrib import admin

from apps.base.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)


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
                    'get_tags', 'created_at', 'get_favorites_count')
    search_fields = ('name', 'author__username', 'author__first_name',
                     'author__last_name')
    list_filter = ('tags',)
    empty_value_display = EMPTY_MSG

    @admin.display(description="в избранном")
    def get_favorites_count(self, obj):
        return obj.favorite.count()

    @admin.display(description='Никнейм автора')
    def get_author(self, obj):
        return obj.author.username

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        tags = [tag.name for tag in obj.tags.all()]
        return ', '.join(tags)


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'target', 'created_at',)
    search_fields = ('subscriber__username', 'subscriber__username',)
    empty_value_display = EMPTY_MSG


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = EMPTY_MSG


@admin.register(ShoppingCart)
class SoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = EMPTY_MSG
