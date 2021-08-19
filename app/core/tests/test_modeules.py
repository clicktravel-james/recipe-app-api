from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "jimmy.jenkins@click.com"
        password = "Password1"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normilised(self):
        """Test for email normilisation"""
        email = 'test@clickTRAVEL.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEquals(user.email, email.lower())

    def test_new_user_email_invalid_email(self):
        """Test for email validation"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_super_user(self):
        """Test for creating  a super user"""
        user = get_user_model().objects.create_superuser(
            "james.b@matrix.com",
            "Password1"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
