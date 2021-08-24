from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

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
