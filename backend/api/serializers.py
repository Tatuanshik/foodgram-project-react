from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (ModelSerializer,
                                        UniqueTogetherValidator)
from rest_framework.fields import SerializerMethodField
from recipes.models import (Ingredient, Recipe, Favorite, TagRecipe,
                            Tag, RecipeIngredient, ShoppingList)
from users.models import User, Followers


class UsersCreateSerializer(UserCreateSerializer):
    """отвечает за создание пользователя."""
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise UniqueTogetherValidator(
                'Недопустимое имя пользователя!'
            )
        return value


class UsersSerializer(UserSerializer):
    """отображает пользователя."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        """получаем подписки на автора."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Followers.objects.filter(
            user=request.user, author=obj).exists()


class FollowerSerializer(serializers.ModelSerializer):
    """отображение подписок пользователя."""
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """получаем подписки на автора."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Followers.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        """получаем рецепты."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return UserFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class FollowUsersSerializer(ModelSerializer):
    """отображает подписки."""
    class Meta:
        model = Followers
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Followers.objects.all(),
                fields=('user', 'author'),
            )
        ]

    def validate_data(self):
        author = self.instance
        user = self.context.get('request')
        if Followers.objects.filter(author=author, user=user.user).exists():
            raise UniqueTogetherValidator(
                detail='Вы уже подписаны!',
            )
        if user == author:
            raise UniqueTogetherValidator(
                detail='Подписка на себя запрещена',
            )

    def to_representation(self, instance):
        return UsersSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data


class IngredientSerializer(serializers.ModelSerializer):
    """отображение ингредиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'measurement_unit',
            'name'
        )


class IngredientAddSerializer(serializers.ModelSerializer):
    """добавление ингредиентов"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """для модели Рецептов и Ингредиентов."""
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """отображание тэгов."""
    name = serializers.CharField(
        required=True,
    )
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class UserFavoriteSerializer(serializers.ModelSerializer):
    """отображение избранного."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """для модели Избранного."""
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def get_fav(self, request):
        return Favorite.objects.filter(
            user=request.user, recipe__id=id
        ).exists()

    def to_representation(self, instance):
        return UserFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """для модели Рецепта в корзине."""
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def get_is_list(self, request):
        return ShoppingList.objects.filter(
            user=request.user, recipe=request.recipe
        ).exists()

    def to_representation(self, instance):
        return UserFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class RecipeSerializer(serializers.ModelSerializer):
    """просмотр рецептов."""
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    author = UsersSerializer(required=True)
    is_favorited = SerializerMethodField(method_name='get_favorited')
    is_in_shopping_cart = SerializerMethodField(method_name='get_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'image',
            'name',
            'text',
            'author',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'measurement_unit', 'name',
            amount=F('recipeingredient__amount')
        )
        return ingredients

    def get_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """изменение/создание рецепта."""
    ingredients = IngredientAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'ingredients',
            'tags',
            'text',
            'image',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data["ingredients"]
        ingredients_list = []
        for ingredient in ingredients:
            if not ingredients:
                raise serializers.ValidationError(
                    'Нужен минимум 1 ингредиент в рецепте!')
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!')
            if int(ingredient.get('amount')) > 1000:
                raise serializers.ValidationError(
                    'Количество ингредиента не должно быть больше 1000!'
                )
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным!'
                )
            ingredients_list.append(ingredient_id)
        return data

    def validate_tags(self, tags):
        """валидация тегов."""
        if not tags:
            raise serializers.ValidationError(
                'Нужно выбрать хотя бы один тег!')
        tags_list = []
        for tag in tags:
            if tag not in Tag.objects.all():
                raise serializers.ValidationError(
                    'Тег не найден!'
                )
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Теги должны быть уникальными!'
                )
            tags_list.append(tag)
        return tags

    def create_ingredients(self, ingredients, recipe):
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            item = RecipeIngredient(
                recipe=recipe,
                amount=ingredient.get('amount'),
                ingredient=ingredient_id
            )
            ingredients_list.append(item)
        RecipeIngredient.objects.bulk_create(ingredients_list)

    def validate_cooking_time(self, cooking_time):
        """валидация времени приготовления."""
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления меньше 1!')
        if int(cooking_time) > 1000:
            raise serializers.ValidationError(
                'Время приготовления больше 1000!')
        if not int(cooking_time):
            raise serializers.ValidationError(
                'Можно ввести только число!')
        return cooking_time

    def create(self, validated_data):
        """создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """редактирование рецепта."""
        TagRecipe.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(ingredients, instance)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data
