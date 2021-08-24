from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users public API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a new valid user"""
        """Given """
        payload = {
            'email': 'jimmyjenkins@borderlands.com',
            'password': 'Password1',
            'name': 'Jimmy Jenkins',
        }

        """When"""
        res = self.client.post(CREATE_USER_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        """Given """
        payload = {
            'email': 'jimmyjenkins@borderlands.com',
            'password': 'Password1',
            'name': 'Jimmy Jenkins',
        }
        create_user(**payload)

        """When"""
        res = self.client.post(CREATE_USER_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that you cannot create a user with a very short password"""
        """Given """
        payload = {
            'email': 'jimmyjenkins@borderlands.com',
            'password': 'god',
            'name': 'Jimmy Jenkins',
        }

        """When"""
        res = self.client.post(CREATE_USER_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        does_user_exist = get_user_model().objects.filter(
            email='jimmyjenkins@borderlands.com'
        ).exists()
        self.assertFalse(does_user_exist)

    def test_create_token_for_user(self):
        """Test for generating a token for a valid user"""
        """Given """
        payload = {
            'email': 'jimmyjenkins@borderlands.com',
            'password': 'Password1',
        }
        create_user(**payload)

        """When"""
        res = self.client.post(TOKEN_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_for_invlaid_credentails(self):
        """Test that we get an error response for token if password wrong"""
        """Given """
        user_email = 'jimmyjenkins@borderlands.com'
        create_user(email=user_email, password='Password1')
        payload = {
            'email': user_email,
            'password': 'wrong',
        }

        """When"""
        res = self.client.post(TOKEN_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_for_mising_user(self):
        """Test for error response requesting token with no user"""
        """Given """
        payload = {
            'email': 'jimmyjenkins@borderlands.com',
            'password': 'Password1',
        }

        """When"""
        res = self.client.post(TOKEN_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_for_missing_request_fields(self):
        """Test that we get an error response for token if no password"""
        """Given """
        payload = {
            'email': 'jimmyjenkins@borderlands.com',
            'password': '',
        }

        """When"""
        res = self.client.post(TOKEN_URL, payload)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_auth_is_needed_to_get_a_users_details(self):
        """Test that a user needs authentication to get the details"""
        """When"""
        res = self.client.get(ME_URL)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """"Tests for the the Users private API"""

    def setUp(self):
        self.user = create_user(
            email='test.jenkins@clicktravel.com',
            password='testpass',
            name='My Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_a_users_details_are_returned_with_authed_get_request(self):
        """Test that with authorisation the user detail's are returned"""
        """When"""
        res = self.client.get(ME_URL)

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_posting_to_a_user_is_not_allowed(self):
        """Test that you cannot create a user via post"""
        """When"""
        res = self.client.post(ME_URL, {})

        """Then"""
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_users_profile(self):
        """Test you can update a user when authenticated"""
        """Given """
        payload = {
            'name': 'Jimmo Jenkins',
            'password': 'Password1',
        }

        """When"""
        res = self.client.patch(ME_URL, payload)

        """Then"""
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
