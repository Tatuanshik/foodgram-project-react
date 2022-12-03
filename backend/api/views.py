from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response
from recipes.models import (Ingredient, RecipeIngredient, Recipe,
                            ShoppingList, Tag, Favorite)
from users.models import Followers
from .filters import RecipeFilter, IngredientSearchFilter
from .paginations import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer, UsersSerializer,
                          FollowUsersSerializer, FavoriteSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingListSerializer, FollowerSerializer)


User = get_user_model()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backend = [DjangoFilterBackend, IngredientSearchFilter]
    search_fields = ('^name', 'name')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @action(methods=['GET'], detail=False, url_path='me',)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersView(APIView):
    queryset = Followers.objects.all()
    permission_classes = (IsAuthenticated, )

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id
        }
        serializer = FollowUsersSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Followers, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFollowView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = FollowerSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class FavoriteViewSet(APIView):
    queryset = Favorite.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingListView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        serializer = ShoppingListSerializer(
            data=data, context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingList.objects.filter(
                user=request.user, recipe=recipe
            ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_list(request):
    ingredient_list = 'Cписок покупок:'
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    for num, i in enumerate(ingredients):
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        if num < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
