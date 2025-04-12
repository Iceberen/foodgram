from apps.accounts.views import (CustomTokenCreateView, CustomTokenDestroyView,
                                 CustomUserViewSet)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('auth/token/login/', CustomTokenCreateView.as_view(),
         name='token_create'),
    path('auth/token/logout/', CustomTokenDestroyView.as_view(),
         name='token_delete'),
    path('', include(router.urls)),
    path('users/', include('djoser.urls')),
]
