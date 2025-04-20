from django.urls import include, path
from rest_framework import routers

from .views import (IngredientView, RecipesViewSet, TagView,
                    CustomTokenCreateView, CustomTokenDestroyView,
                    CustomUserViewSet)

router = routers.DefaultRouter()
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagView, basename='tags')
router.register('ingredients', IngredientView, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', CustomTokenCreateView.as_view(),
         name='token_create'),
    path('auth/token/logout/', CustomTokenDestroyView.as_view(),
         name='token_delete'),
    path('users/', include('djoser.urls')),
]
