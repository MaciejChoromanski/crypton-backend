from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestAdminSite(TestCase):
    """Tests Admin site display features"""

    def setUp(self) -> None:
        """Creates Users for the tests"""

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username='test_admin',
            email='admin@testdomain.com',
            password='test_password',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            username='test_username',
            email='test@testdomain.com',
            password='test_password',
        )

    def test_users_listed(self) -> None:
        """Tests if Users are listed properly"""

        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.crypto_key)

    def test_user_change_page(self) -> None:
        """Tests if change_page for the User works properly"""

        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self) -> None:
        """Tests if add_page for the User works properly"""

        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
