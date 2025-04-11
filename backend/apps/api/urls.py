from django.urls import include, path
from rest_framework import routers

from .views import IngredientView, RecipesViewSet, TagView, recipe_by_link

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipe')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
    path('s/<uuid:short_link>/', recipe_by_link, name='recipe-short-link'),
]
