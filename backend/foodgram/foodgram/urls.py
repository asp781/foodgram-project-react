from django.contrib import admin
from django.urls import path, include, re_path
from api.views import (
    IngredientViewSet, RecipeViewSet, SubscribeViewSet, SubscriptionViewSet,
    TagViewSet
)
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', SubscribeViewSet)


admin.site.site_header = 'Продуктовый помощник'
admin.site.index_title = 'Панель администратора'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/subscriptions/', SubscriptionViewSet.as_view(
        {'get': 'list'}
    )),
    path('api/', include('djoser.urls')),
    re_path(r'^api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
    # path('api/v1/drf-auth/', include('rest_framework.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
