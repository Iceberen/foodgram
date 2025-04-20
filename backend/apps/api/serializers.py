from drf_extra_fields.fields import Base64ImageField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from apps.recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                                ShoppingCart, Tag)
from apps.accounts.models import Subscription

User = get_user_model()


class TokenCreateSerializer(serializers.Serializer):
    """Сериализатор создания токена."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True)


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""

    password = serializers.CharField(min_length=settings.MIN_PASSWORD_LENGTH,
                                     write_only=True, required=True)
    first_name = serializers.CharField(required=True,
                                       max_length=settings.MAX_LENTHG_NAME)
    last_name = serializers.CharField(required=True,
                                      max_length=settings.MAX_LENTHG_NAME)
    email = serializers.EmailField(max_length=settings.MAX_LENTGHT_EMAIL,
                                   required=True,
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all(),
                                       message='Почта уже занята')])
    username = serializers.CharField(
        max_length=settings.MAX_LENTHG_NAME,
        required=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+$',
                           message=('Никнейм может содержать только цифры,'
                                    'буквы и символы: . @ + -')),
            UniqueValidator(queryset=User.objects.all(),
                            message='Никнейм уже занят')])

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        validate_password(password, user)
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
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar',)


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор изменения аватара."""

    avatar = Base64ImageField()

    class Meta:

        model = User
        fields = ('avatar',)


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля."""

    new_password = serializers.CharField(
        min_length=settings.MIN_PASSWORD_LENGTH,
        style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

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
                'current_password': 'Старый пароль неверный'})
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                'new_password': 'Пароли не должны совпадать'})
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор представления ингредиентов при предствлении рецепта."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = ReadRecipeIngredientSerializer(many=True, read_only=True,
                                                 source='recipe_ingredients',)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and getattr(obj, 'favorite').filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and getattr(obj, 'in_shopping_cart')
            .filter(user=request.user).exists()
        )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time', )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецепта."""

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиентов при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient',
                                            required=True)
    amount = serializers.IntegerField(required=True,
                                      min_value=settings.MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = CreateRecipeIngredientSerializer(required=True, many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=True)
    name = serializers.CharField(required=True,
                                 max_length=settings.MAX_LENTHG_RECIPE)
    cooking_time = serializers.IntegerField(min_value=settings.MIN_TIME,
                                            required=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'author'
        )
        read_only_fields = ('author',)

    def _create_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.recipe_ingredients.all().delete()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self._create_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate_image(self, value):
        if not self.instance and not value:
            raise serializers.ValidationError(
                'Изображение обязательно при создании.')
        return value

    def _check_unique(self, items, field_name):
        ids = [item.id if hasattr(item, 'id') else item.get('ingredient').id
               for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {field_name:
                    f'{field_name.capitalize()} должны быть уникальными.'})

    def _check_required(self, attrs, field_name):
        if field_name not in attrs or not attrs[field_name]:
            raise serializers.ValidationError(
                {field_name:
                    f'{field_name.capitalize()} Обязательное поле.'})

    def validate(self, attrs):
        self._check_required(attrs, 'tags')
        self._check_required(attrs, 'ingredients')
        self._check_unique(attrs['tags'], 'tags')
        self._check_unique(attrs['ingredients'], 'ingredients')
        return attrs

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [UniqueTogetherValidator(queryset=Favorite.objects.all(),
                                              fields=('user', 'recipe'), )]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для управления корзиной пользователя."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
        validators = [UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe'), )]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context).data


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
        subscriber, target = attrs['subscriber'], attrs['target']
        if subscriber == target:
            raise serializers.ValidationError('Подписка на самого себя.')
        if Subscription.objects.filter(subscriber=subscriber,
                                       target=target).exists():
            raise serializers.ValidationError('Уже подписан.')
        return attrs

    def to_representation(self, instance):
        return GetFollowSerializer(
            instance.target, context=self.context).data
