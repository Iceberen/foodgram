from django.urls import include, path
from rest_framework import routers

from .views import IngredientView, RecipesViewSet, TagView

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipe')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
