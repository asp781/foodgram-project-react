# Generated by Django 2.2.19 on 2023-01-30 00:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230128_0937'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('-created',), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'ordering': ('pk',), 'verbose_name': 'Ингредиент рецепта', 'verbose_name_plural': 'Ингредиенты рецепта'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'ordering': ('-created',), 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списоки покупок'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('-created',), 'verbose_name': 'Подписки', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('pk',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(3000, message='Максимальное количество 3000'), django.core.validators.MinValueValidator(1, message='Минимальное количество 1')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(600, message='Максимальное время 600 мин'), django.core.validators.MinValueValidator(1, message='Минимальное время 1 мин')], verbose_name='Время приготовления'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='user_recipe_shopping'),
        ),
    ]
