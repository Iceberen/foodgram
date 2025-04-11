from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, TokenDestroyView, UserViewSet

from apps.base.pagination import Pagination
from apps.base.permissions import IsOwnerOrReadOnly
from apps.accounts.serializers import (
    CreateUserSerializer, CustomUserSerializer, UserAvatarSerializer,
    ChangePasswordSerializer, GetFollowSerializer, FollowSerializer
)
from apps.base.models import Subscription


User = get_user_model()


class CustomTokenCreateView(TokenCreateView):
    """Кастомное получение токена."""

    permission_classes = (AllowAny, )

    def _action(self, serializer):
        try:
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = User.objects.get(email=email)
            user = authenticate(username=email, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'auth_token': token.key,
                }, status=status.HTTP_200_OK)
            return Response({
                'error': 'Неверные учетные данные'
            }, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({
                'error': 'Пользователь с таким email не найден'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)


class CustomTokenDestroyView(TokenDestroyView):
    """Кастомное удаление токена."""

    def delete(self, request):
        try:
            token = request.auth
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    pagination_class = Pagination

    def get_permissions(self):
        """Получение класса ограничения."""
        if self.action in ('list', 'retrieve', 'create'):
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        """Получение класса сериализатора."""
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        elif self.action == 'create':
            return CreateUserSerializer
        return super().get_serializer_class()

    @action(methods=('GET',), detail=False, url_path='me',
            permission_classes=(IsAuthenticated,),)
    def me(self, request):
        """Получение текущего пользователя."""
        serializer = CustomUserSerializer(request.user,
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('PUT', 'DELETE',), detail=False, url_path='me/avatar',
            permission_classes=(IsAuthenticated,), )
    def user_avatar(self, request):
        """Добавления и удаление аватара."""
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            if not avatar_data:
                return Response(
                    {'avatar': 'Поле avatar пустое!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserAvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('POST', ), url_path='set_password',
            permission_classes=(IsOwnerOrReadOnly, ), )
    def set_password(self, request):
        """Кастомное изменение пароля."""
        serializer = ChangePasswordSerializer(data=request.data,
                                              context={'request': request})
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        new_password = serializer.validated_data['new_password']
        request.user.set_password(new_password)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False, url_path='subscriptions',
            permission_classes=(IsAuthenticated,), )
    def get_subscriptions(self, request):
        """Получение списка подписок."""
        following_users = User.objects.filter(
            subscribers__subscriber=request.user
        ).distinct()
        paginator = Pagination()
        result_page = paginator.paginate_queryset(following_users, request)
        serializer = GetFollowSerializer(
            result_page,
            many=True,
            context={'request': request,
                     'recipes_limit': request.query_params.get('recipes_limit')
                     },
        )
        return paginator.get_paginated_response(serializer.data)

    @action(methods=('POST', 'DELETE',), detail=True, url_path='subscribe',
            permission_classes=(IsAuthenticated,), )
    def subscribe(self, request, id):
        """Подписка/отписка на пользователя."""
        user = get_object_or_404(User, username=request.user.username)
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'subscriber': user.id, 'target': following.id},
                context={
                    'request': request,
                    'recipes_limit': request.query_params.get('recipes_limit')}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            follow = Subscription.objects.filter(subscriber=user.id,
                                                 target=following.id,)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
