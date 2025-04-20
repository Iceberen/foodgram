from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, Recipe, ShoppingCart, Tag,
                     RecipeIngredient)

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


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1

    def has_add_permission(self, request, obj=None):
        if obj is not None and obj.recipe_ingredients.count() == 0:
            return False
        return super().has_add_permission(request, obj)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'text', 'cooking_time',
                    'get_tags', 'created_at', 'get_favorites_count',
                    'get_ingredients', 'get_image')
    search_fields = ('name', 'author__username', 'author__first_name',
                     'author__last_name')
    list_filter = ('tags',)
    empty_value_display = EMPTY_MSG
    inlines = (RecipeIngredientInline,)

    @admin.display(description="в избранном")
    def get_favorites_count(self, obj):
        return obj.favorite.count()

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        tags = [tag.name for tag in obj.tags.all()]
        return ', '.join(tags)

    @admin.display(description="ингредиенты")
    @mark_safe
    def get_ingredients(self, obj):
        if not obj.recipe_ingredients.exists():
            return "Нет ингредиентов"
        return "<br>".join(
            [
                f"{item.ingredient.name} - "
                f"{item.amount} "
                f"{item.ingredient.measurement_unit}"
                for item in obj.recipe_ingredients.all()
            ]
        )

    @admin.display(description="изображение")
    @mark_safe
    def get_image(self, obj):
        if not obj.image:
            return "Нет изображения"
        return f'<img src="{obj.image.url}" width="100">'


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
