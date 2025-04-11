from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from core.settings import MIN_TIME, MIN_AMOUNT, MAX_LENTHG_RECIPE
from apps.accounts.serializers import CustomUserSerializer
from apps.base.models import (Tag, Ingredient, RecipeIngredient, Recipe,
                              Favorite, ShoppingCart)


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
    amount = serializers.IntegerField(read_only=True)

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
    amount = serializers.IntegerField(required=True, min_value=MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = CreateRecipeIngredientSerializer(required=True, many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=True)
    text = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=MAX_LENTHG_RECIPE)
    cooking_time = serializers.IntegerField(min_value=MIN_TIME, required=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'author'
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.recipe_ingredients.all().delete()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data

    def validate(self, attrs):
        if 'tags' not in attrs or not attrs['tags']:
            raise serializers.ValidationError({'tags': 'Обязательное поле.'})
        if 'ingredients' not in attrs or not attrs['ingredients']:
            raise serializers.ValidationError(
                {'ingredients': 'Обязательное поле.'})
        tag_id_list = [tag.id for tag in attrs['tags']]
        if len(tag_id_list) != len(set(tag_id_list)):
            raise serializers.ValidationError(
                {'tags': 'Тэги должны быть уникальными.'})
        ingredient_id_list = [
            ingred.get('ingredient').id for ingred in attrs['ingredients']]
        if len(ingredient_id_list) != len(set(ingredient_id_list)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты должны быть уникальными.'})
        if 'image' not in attrs or not attrs['image']:
            raise serializers.ValidationError({'image': 'Обязательное поле.'})
        return attrs


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [UniqueTogetherValidator(queryset=Favorite.objects.all(),
                                              fields=('user', 'recipe'),),]

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
            fields=('user', 'recipe'),),]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context).data
