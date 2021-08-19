from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objecs.create_superuser(
            email='admin@clickravel.com',
            password='Password123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='firstUser@clicktravel.com',
            password='Password1',
            name='Jimmy Jenkins'
        )

def test_users_listed(self):
    """Test that users are listed in the user page"""
    url = reverse('admin:core_user_changelist')
    res = self.client.get(url)

    self.assertConatins(res, self.user.name)
    self.assertConatins(res, self.user.email)
