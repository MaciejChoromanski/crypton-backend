from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import User

CREATE_USER_URL = reverse('api:user_create')
ME_URL = reverse('api:user_me')


def create_user(**params) -> User:
    """Creates a User"""

    return get_user_model().objects.create_user(**params)


class TestPublicUserApi(TestCase):
    """Tests for the public API for the User model"""

    def setUp(self) -> None:
        """Sets APIClient for the tests"""

        self.client = APIClient()

    def test_create_valid_user_success(self) -> None:
        """Tests if a User is properly created"""

        payload = {
            'email': 'test@testdomain.com',
            'password': 'test_password',
            'username': 'test_username',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self) -> None:
        """Tests what happens when a User is created twice"""

        payload = {
            'email': 'test@testdomain.com',
            'password': 'test_password',
            'username': 'test_username',
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self) -> None:
        """Tests what happens when a password is too short"""

        payload = {
            'email': 'test@testdomain.com',
            'password': 'pass',
            'username': 'test_username',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = (
            get_user_model().objects.filter(email=payload['email']).exists()
        )

        self.assertFalse(user_exists)

    def test_retrieve_user_forbidden(self) -> None:
        """
        Tests what happens when not authenticated User requests 'user_me' view
        """

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestPrivateUserApi(TestCase):
    """Tests for the private API for the User model"""

    def setUp(self) -> None:
        """Creates and authenticates User for the tests"""

        self.user = create_user(
            email='test@testdomain.com',
            password='test_password',
            username='test_username',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self) -> None:
        """Tests if User's info is retrieved successfully"""

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {'username': self.user.username, 'email': self.user.email},
        )

    def test_post_me_not_allowed(self) -> None:
        """Tests if POST is not allowed for the 'user_me' view"""

        response = self.client.post(ME_URL, {})

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self) -> None:
        """Tests if User's profile is updated successfully"""

        payload = {'password': 'new_password', 'username': 'new_username'}
        response = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self) -> None:
        """Tests if User is deleted successfully"""

        response = self.client.delete(ME_URL)
        user_exists = User.objects.filter(username=self.user.username).exists()

        self.assertFalse(user_exists)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
