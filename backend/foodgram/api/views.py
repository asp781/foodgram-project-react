from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from core import pdf
from recipes.filters import RecipeFilter
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from recipes.paginators import CustomPagination
from users.models import User
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    ordering = ('-created',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        if self.request.method == 'POST':
            return RecipeCreateSerializer
        if self.request.method == 'PATCH':
            return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors':
                            'Рецепт уже у вас в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=user, recipe=recipe)
        queryset = Favorite.objects.get(user=request.user.id, recipe=recipe.id)
        serializer = FavoriteSerializer(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_del(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Этого рецепта нет в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors':
                            'Рецепт уже у вас в список покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=user, recipe=recipe)
        queryset = ShoppingCart.objects.get(
            user=request.user.id, recipe=recipe.id
        )
        serializer = ShoppingCartSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shopping_cart_del(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Этого рецепта нет в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def make_pdf(self, header, data, filename, http_status):
        site_name = settings.SITE_NAME
        pdf_data = [
            (pdf.Constant.DT_CAPTION, 'Мой список покупок:'),
            (pdf.Constant.DT_EMPTYLINE, '')
        ]
        for ingredient in data:
            pdf_data.append((
                pdf.Constant.DT_TEXT,
                '{name} - {amount}{measurement_unit}'.format(
                    name=ingredient['ingredients__name'],
                    amount=ingredient['amount'],
                    measurement_unit=ingredient[
                        'ingredients__measurement_unit'
                    ]
                )))
        pdf_obj = pdf.PDFMarker()
        pdf_obj.data = pdf_data
        pdf_obj.footer_text = f'Список покупок с сайта {site_name}'

        content = pdf_obj.pdf_render()
        response = HttpResponse(
            content=content,
            content_type='application/pdf',
            status=http_status)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        recipes = request.user.shopping_cart.all().values('recipe_id')
        ingredients = IngredientRecipe.objects.filter(recipes__in=recipes)
        if not ingredients:
            return Response(
                {'errors': 'Список пуст'}, status=status.HTTP_204_NO_CONTENT
            )
        total_ingredients = ingredients.values(
            'ingredients__name', 'ingredients__measurement_unit').order_by(
            'ingredients__name').annotate(amount=Sum('amount'))
        return self.make_pdf(
            ('Наименование', 'Количество', 'Ед.измерения'),
            total_ingredients,
            'shoppingcart.pdf',
            status.HTTP_200_OK
        )


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        follower = self.request.user
        return Subscription.objects.filter(follower=follower)


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        follower = request.user
        author = get_object_or_404(User, pk=pk)
        if follower == author:
            return Response({'errors':
                            'Вы не можете подписаться на себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(
            follower=follower, author=author
        ).exists():
            return Response({'errors':
                            'Вы уже подписаны на автора.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(follower=follower, author=author)
        queryset = Subscription.objects.get(
            follower=request.user.id, author=author.id
        )
        serializer = SubscriptionSerializer(
            queryset, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_del(self, request, pk=None):
        follower = request.user
        author = get_object_or_404(User, pk=pk)
        if not Subscription.objects.filter(
            follower=follower, author=author
        ).exists():
            return Response({'errors': 'Вы не подписаны на автора.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.get(follower=follower, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
