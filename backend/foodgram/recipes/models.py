from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Тэг')
    color = models.CharField(
        max_length=7, verbose_name='Цветовой HEX-код', default='#ABCDEF'
    )
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('pk',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Наименование', db_index=True
    )
    measurement_unit = models.CharField(
        max_length=50, verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото рецепта',
    )
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', through='IngredientRecipe'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        default=1, verbose_name='Время приготовления',
        validators=[
            MaxValueValidator(600, message='Максимальное время 600 мин'),
            MinValueValidator(1, message='Минимальное время 1 мин')
        ]
    )
    created = models.DateTimeField(
        'Дата публикации', auto_now_add=True, null=True
    )
    is_favorited = models.BooleanField(null=True)
    is_in_shopping_cart = models.BooleanField(null=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.SET_NULL, null=True,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        default=1, verbose_name='Количество',
        validators=[
            MaxValueValidator(3000, message='Максимальное количество 3000'),
            MinValueValidator(1, message='Минимальное количество 1')
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('pk',)

    def __str__(self):
        return f'Ингредиент из рецепта {self.recipes.name}'


class Subscription(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    created = models.DateTimeField(
        'Дата публикации', auto_now_add=True, null=True
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'], name='follower_author'
            )
        ]

    def __str__(self):
        return f'{self.follower} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Рецепт'
    )
    created = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Рецепт'
    )
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списоки покупок'
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_recipe_shopping'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
