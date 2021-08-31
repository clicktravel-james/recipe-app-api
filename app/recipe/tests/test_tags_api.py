from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


class PublicTagsTagApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required_for_tags(self):
        res = self.client.get(TAGS_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com'
            "Password1"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_tags(self):
        """Given"""
        Tag.objects.create(user=self.user, name="Meat")
        Tag.objects.create(user=self.user, name="Fish")

        """When"""
        res = self.client.get(TAGS_URL)

        """Then"""
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_should_have_tags_for_authenticated_user(self):
        """Given"""
        unauthenticated_user = get_user_model().objects.create_user(
            'test2@test.com'
            "Password1"
        )
        Tag.objects.create(user=unauthenticated_user, name="Ice Cream")
        tag = Tag.objects.create(user=self.user, name="Fruity")

        """When"""
        res = self.client.get(TAGS_URL)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Given"""
        payload = {
            'name': 'This is a test tag'
        }

        """When"""
        self.client.post(TAGS_URL, payload)

        """Then"""
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid_payload(self):
        """Given"""
        payload = {
            'name': ''
        }

        """When"""
        res = self.client.post(TAGS_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieved_tags_assigned_to_a_recipe(self):
        """Given"""
        tag1 = Tag.objects.create(user=self.user, name="Ice Cream")
        tag2 = Tag.objects.create(user=self.user, name="Fruity")
        recipe = Recipe.objects.create(
            title='Ice cream sunday',
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        """When"""
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        """Then"""
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieved_tags_assigned_unique(self):
        """Given"""
        tag = Tag.objects.create(user=self.user, name="Ice Cream")
        Tag.objects.create(user=self.user, name="Fruity")
        recipe1 = Recipe.objects.create(
            title='Ice cream sunday',
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Ice cream cake',
            time_minutes=5,
            price=15.00,
            user=self.user,
        )
        recipe2.tags.add(tag)

        """When"""
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        """Then"""
        self.assertEqual(len(res.data), 1)
