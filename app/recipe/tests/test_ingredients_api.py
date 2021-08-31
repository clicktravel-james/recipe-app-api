from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required_for_getting_ingredients(self):
        """When"""
        res = self.client.get(INGREDIENTS_URL)

        """Then"""
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com'
            "Password1"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_an_ingredient(self):
        """Given"""
        Ingredient.objects.create(user=self.user, name="Orange")
        Ingredient.objects.create(user=self.user, name="Salmon")

        """When"""
        res = self.client.get(INGREDIENTS_URL)

        """Then"""
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_should_only_have_ingredients_for_authenticated_user(self):
        """Given"""
        unauthenticated_user = get_user_model().objects.create_user(
            'test2@test.com'
            "Password1"
        )
        Ingredient.objects.create(user=unauthenticated_user, name="Nerdz")
        ingredient = Ingredient.objects.create(user=self.user, name="Cherry")

        """When"""
        res = self.client.get(INGREDIENTS_URL)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Given"""
        payload = {
            'name': 'This is a test ingredient'
        }

        """When"""
        self.client.post(INGREDIENTS_URL, payload)

        """Then"""
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid_payload(self):
        """Given"""
        payload = {
            'name': ''
        }

        """When"""
        res = self.client.post(INGREDIENTS_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieved_ingredients_assigned_to_a_recipe(self):
        """Given"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Orange")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Salmon")
        recipe = Recipe.objects.create(
            title='Orange cheesecake',
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)

        """When"""
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        """Then"""
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieved_ingredients_assigned_unique(self):
        """Given"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Orange")
        Ingredient.objects.create(user=self.user, name="Salmon")
        recipe1 = Recipe.objects.create(
            title='Ice cream sunday',
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe1.ingredients.add(ingredient1)
        recipe2 = Recipe.objects.create(
            title='Ice cream cake',
            time_minutes=5,
            price=15.00,
            user=self.user,
        )
        recipe2.ingredients.add(ingredient1)

        """When"""
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        """Then"""
        self.assertEqual(len(res.data), 1)
