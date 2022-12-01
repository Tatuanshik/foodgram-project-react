from django.contrib import admin
from .models import (Ingredient, Recipe, Tag, Favorite,
                     RecipeIngredient, ShoppingList,)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'name',)
    inlines = (IngredientInLine,)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'

    def is_favorited(self, obj):
        return obj.favorites.count()

    is_favorited.short_description = 'В избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')
    empty_value_display = '-пусто-'


admin.site.register(ShoppingList)
