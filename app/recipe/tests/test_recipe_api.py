from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def create_recipe_details_url(recipe_id):
    """Function for creating a dynamic url for recipe details"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Starter'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Nutmeg'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""

    defaults = {
        'title': 'Default Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required_for_getting_recipes(self):
        """When"""
        res = self.client.get(RECIPES_URL)

        """Then"""
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com'
            "Password1"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_an_recipe(self):
        """Given"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        """When"""
        res = self.client.get(RECIPES_URL)

        """Then"""
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_should_have_recipe_for_authenticated_user(self):
        """Given"""
        unauthenticated_user = get_user_model().objects.create_user(
            'test2@test.com'
            "Password1"
        )
        sample_recipe(user=unauthenticated_user)
        sample_recipe(user=self.user)

        """When"""
        res = self.client.get(RECIPES_URL)

        """Then"""
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_should_view_a_recipe_details(self):
        """Given"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        ingredient = sample_ingredient(user=self.user)
        recipe.tags.add(tag)
        recipe.ingredients.add(ingredient)

        url = create_recipe_details_url(recipe.id)

        """When"""
        res = self.client.get(url)

        """Then"""
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_should_create_a_basic_recipe(self):
        """Given"""
        payload = {
            'title': 'Chocolate fudge cake',
            'time_minutes': 45,
            'price': 5.00,
        }

        """When"""
        res = self.client.post(RECIPES_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_should_create_a_recipe_with_tags(self):
        """Given"""
        tag1 = sample_tag(user=self.user, name='Desert')
        tag2 = sample_tag(user=self.user, name='Nut dish')

        payload = {
            'title': 'Carrot cake',
            'time_minutes': 50,
            'price': 10.00,
            'tags': [tag1.id, tag2.id],
        }

        """When"""
        res = self.client.post(RECIPES_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_should_create_a_recipe_with_ingredients(self):
        """Given"""
        ingredient1 = sample_ingredient(user=self.user, name='Rice')
        ingredient2 = sample_ingredient(user=self.user, name='Chicken')

        payload = {
            'title': 'Chicken curry',
            'time_minutes': 30,
            'price': 10.00,
            'ingredients': [ingredient1.id, ingredient2.id],
        }

        """When"""
        res = self.client.post(RECIPES_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_should_partial_update_recipe(self):
        """Given"""
        recipe = sample_recipe(user=self.user)
        tag1 = sample_tag(user=self.user, name='Fish dish')

        payload = {
            'title': 'Seafood pie',
            'tags': [tag1.id],
        }
        url = create_recipe_details_url(recipe_id=recipe.id)

        """When"""
        self.client.patch(url, payload)

        """Then"""
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(tag1, tags)

    def test_should_update_all_recipe(self):
        """Given"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Naga curry',
            'time_minutes': 28,
            'price': 9.00,
        }
        url = create_recipe_details_url(recipe_id=recipe.id)

        """When"""
        self.client.put(url, payload)

        """Then"""
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
