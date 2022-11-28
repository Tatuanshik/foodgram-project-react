from django_filters import rest_framework as filter, filters
from rest_framework.filters import SearchFilter
from recipes.models import Recipe, Ingredient
from users.models import User


class RecipeFilter(filter.FilterSet):
    author = filter.ModelChoiceFilter(
            queryset=User.objects.all())
    tags = filter.AllValuesMultipleFilter(
            field_name='tags__slug'
    )
    is_favorited = filter.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = filter.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientSearchFilter(SearchFilter):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
