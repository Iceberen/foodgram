from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from foodgram.settings import MAX_LENGTH_SLUG, MAX_LENTHG_NAME, MIN_AMOUNT

User = get_user_model()


class TimeStampModel(models.Model):
    """Базовая абстракная модель."""
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
    )

    class Meta:
        abstract = True


class Ingredient(models.Model):
    """Модель Ингредиентов."""
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=MAX_LENTHG_NAME,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=MAX_LENGTH_SLUG,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(TimeStampModel):
    """Модель Тэгов."""
    name = models.CharField(
        verbose_name='Тэг',
        max_length=MAX_LENTHG_NAME,
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Для создания слага используйте буквы, числа и _',), ],
        verbose_name='Slug тэга',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(TimeStampModel):
    """Модель Рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Рецепт',
        max_length=MAX_LENTHG_NAME
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipe_images/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at', )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецептов и ингредиентов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        blank=False,
        null=False,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество/объем',
        default=MIN_AMOUNT,
        validators=[MinValueValidator(MIN_AMOUNT)],
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient.measurement_unit} ' \
            f'{self.ingredient.name}'


class Favorite(TimeStampModel):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        null=True)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Покупка',
        null=True)

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
