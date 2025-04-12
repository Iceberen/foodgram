from apps.base.models import Subscription
from core.settings import (MAX_LENTGHT_EMAIL, MAX_LENTHG_NAME,
                           MIN_PASSWORD_LENGTH)
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

User = get_user_model()


class TokenCreateSerializer(serializers.Serializer):
    """Сериализатор создания токена."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                {'email': 'Пользователь с таким email не найден'}
            )
        user = authenticate(username=email, password=password)
        if not user:
            raise ValidationError({'password': 'Неверный пароль'})

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return {'auth_token': token.key}


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""

    password = serializers.CharField(
        min_length=MIN_PASSWORD_LENGTH, write_only=True, required=True,
    )
    first_name = serializers.CharField(
        required=True, max_length=MAX_LENTHG_NAME,
    )
    last_name = serializers.CharField(
        required=True, max_length=MAX_LENTHG_NAME,
    )
    email = serializers.EmailField(
        max_length=MAX_LENTGHT_EMAIL,
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Почта уже занята'
        )]
    )
    username = serializers.CharField(
        max_length=MAX_LENTHG_NAME,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=('Никнейм может содержать только цифры,'
                         'буквы и символы: . @ + -')
            ),
            UniqueValidator(
                queryset=User.objects.all(),
                message='Никнейм уже занят'
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор получения инфо о юзере."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_followed',
    )
    avatar = Base64ImageField()

    def get_is_followed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.subscriptions.filter(target=obj).exists()
        )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор изменения аватара."""

    avatar = Base64ImageField()

    class Meta:

        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор изменения пароля."""

    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = (
            'current_password', 'new_password'
        )

    def validate_new_password(self, value):
        """Валидация new_password."""
        try:
            validate_password(value)
        except ValidationError as err:
            raise serializers.ValidationError(
                {'new_password': list(err.messages)}
            )
        return value

    def validate(self, data):
        """Проверка на совпадение паролей"""
        if not self.context.get('request').user.check_password(
            data['current_password']
        ):
            raise serializers.ValidationError({
                'current_password': 'Старый пароль неверный'
            })
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                'new_password': 'Пароли не должны совпадать'
            })
        return data


class GetFollowSerializer(CustomUserSerializer):
    """Сериализатор получения подписок пользователя."""

    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count',
    )

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipe(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.GET.get('recipes_limit') if request else None
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        from apps.api.serializers import ShortRecipeSerializer
        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор создания/удаления подписок."""

    class Meta:
        model = Subscription
        fields = ('subscriber', 'target',)

    def validate(self, attrs):
        subscriptions, subscribers = attrs['subscriber'], attrs['target']
        if subscriptions == subscribers:
            raise serializers.ValidationError('Подписка на самого себя.')
        if Subscription.objects.filter(subscriber=subscriptions,
                                       target=subscribers).exists():
            raise serializers.ValidationError('Уже подписан.')
        return attrs

    def to_representation(self, instance):
        return GetFollowSerializer(instance.target, context=self.context,).data
