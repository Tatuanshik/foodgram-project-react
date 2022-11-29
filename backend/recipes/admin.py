from django.contrib import admin
from .models import (Ingredient, Recipe, Tag, Favorite,
                     RecipeIngredient, ShoppingList, TagRecipe)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient


class TagInLine(admin.TabularInline):
    model = TagRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    inlines = (IngredientInLine, TagInLine,)

    def is_favorited(self, obj):
        return obj.favorites.count()

    is_favorited.short_description = 'В избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('ingredient',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')
    empty_value_display = '-пусто-'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id',)


admin.site.register(ShoppingList)
