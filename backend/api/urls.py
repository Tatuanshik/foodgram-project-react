from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, TagViewSet, RecipeViewSet, UserViewSet,
                    ShoppingListView, FollowersView, download_shopping_list,
                    UserFollowView, IngredientViewSet)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_list,
        name='download_shopping_cart'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingListView.as_view(),
        name='shopping_cart'
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteViewSet.as_view(),
        name='favorite'
    ),
    path(
        'users/<int:id>/subscribe/',
        FollowersView.as_view(),
        name='subscribe'
    ),
    path(
        'users/subscriptions/',
        UserFollowView.as_view(),
        name='subscriptions'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(v1_router.urls)),
]
