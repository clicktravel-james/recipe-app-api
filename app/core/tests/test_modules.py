from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

from unittest.mock import patch


def sample_user(email='test@lodonboyz.com', password='Password1'):
    return get_user_model().objects.create_user(email, password)


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

    def test_the_tag_string_rep(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Meat'
        )

        self.assertEquals(str(tag), tag.name)

    def test_the_ingredient_string_rep(self):
        """Given"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Becon'
        )

        """Then"""
        self.assertEquals(str(ingredient), ingredient.name)

    def test_the_recipe_string_rep(self):
        """Test the tag string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Meat',
            time_minutes=5,
            price=3.5
        )

        self.assertEquals(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def text_recipe_file_name_uuid(self, mock_uuid):
        """Test for filename unique names"""
        """Given"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'

        """Then"""
        self.assertEqual(file_path, expected_path)




