from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Favorite, Ingredient, IngredientRecipe, Recipe,
    ShoppingCart, Subscription, Tag
)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    fields = ('ingredients', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]
    list_display = (
        'pk', 'name', 'get_html_photo', 'author', 'display_tag',
        'favorite', 'created'
    )
    fields = (
        'name', 'author', 'image', 'get_html_photo', 'text', 'tags',
        'cooking_time', 'favorite'
    )
    readonly_fields = ('get_html_photo', 'favorite', 'display_tag')
    list_filter = ('name', 'author', 'tags',)
    filter_horizontal = ('tags',)
    save_on_top = True

    def get_html_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}' width=50>")

    get_html_photo.short_description = "Миниатюра"

    def favorite(self, object):
        return object.favorites.count()

    favorite.short_description = "Раз в избранном"

    def display_tag(self, object):
        return ', '.join([tag.name for tag in object.tags.all()])

    display_tag.short_description = "Теги"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 200


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe', 'created')
    readonly_fields = ('created',)
    list_filter = ('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'follower', 'author', 'created']
    readonly_fields = ('created',)
    list_filter = ('follower', 'author')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'recipe', 'created']
    readonly_fields = ('created',)
    list_filter = ('user', 'recipe')
