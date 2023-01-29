from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)


class UserListRetrieveSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, object):
        follower = self.context.get('request').user
        if follower.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=follower, author=object.id
        ).exists()


class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredients', queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source='ingredients.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('количество должно больше нуля')
        return value


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserListRetrieveSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        return IngredientAmountSerializer(
            IngredientRecipe.objects.filter(recipes=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipe = obj
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipe = obj
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserListRetrieveSerializer(read_only=True)
    ingredients = IngredientAmountCreateSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'ingredients', 'image', 'name', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart'
        )

    def __is_something(self, obj, model):
        if not self.context['request'].user.is_authenticated:
            return False
        return model.objects.filter(
            recipe=obj, user=self.context['request'].user
        ).exists()

    def get_is_favorited(self, obj):
        return self.__is_something(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.__is_something(obj, ShoppingCart)

    def create(self, validated_data):
        print(validated_data)
        ingredients2 = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print(validated_data)
        obj = Recipe.objects.create(**validated_data)
        obj.tags.set(tags)
        for ingredient1 in ingredients2:
            IngredientRecipe.objects.create(
                recipes=obj,
                ingredients=ingredient1['id'],
                amount=ingredient1['amount']
            )
        return obj

    def update(self, instance, validated_data):
        print(validated_data)
        ingredients2 = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient1 in ingredients2:
            IngredientRecipe.objects.create(
                recipes=instance,
                ingredients=ingredient1['id'],
                amount=ingredient1['amount']
            )

        return instance

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError('должно больше нуля')
        return value


class SimpleRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.StringRelatedField(source='author.email')
    id = serializers.PrimaryKeyRelatedField(source='author.id', read_only=True)
    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (not request.user == obj.author and Subscription.objects.filter(
            follower=request.user, author=obj.author
        ).exists())

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(
                author=obj.author
            ).all()[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(author=obj.author).all()
        serializer = SimpleRecipeSerializer(
            queryset, read_only=True, many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='recipe.name')
    image = serializers.StringRelatedField(
        source='recipe.image', read_only=True
    )
    cooking_time = serializers.StringRelatedField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='recipe.name')
    image = serializers.StringRelatedField(
        source='recipe.image', read_only=True
    )
    cooking_time = serializers.StringRelatedField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
