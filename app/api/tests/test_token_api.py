from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .utils import create_user

CREATE_TOKEN_URL = reverse('api:token')


class TestPublicTokenAPI(TestCase):
    """Tests for the public API for the token authentication"""

    def setUp(self) -> None:
        """Sets up client for the tests"""

        self.client = APIClient()

    def test_create_token_for_user(self):
        """Tests if token ic created successfully"""

        payload = {
            'username': 'test_username',
            'email': 'test@testdomain.com',
            'password': 'test_password',
        }
        create_user(**payload)
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Tests what happens when creating a token
        and the credentials are invalid
        """

        create_user(
            username='test_username',
            email='test@testdomain.com',
            password='test_password'
        )
        payload = {
            'email': 'test@testdomain.com',
            'password': 'wrong_password',
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Tests what happens when creating a token, but the User doesn't exist
        """

        payload = {
            'email': 'test@testdomain.com',
            'password': 'test_password',
        }
        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Tests what happens when one of the fields is missing"""

        response = self.client.post(CREATE_TOKEN_URL, {
            'email': 'something',
            'password': ''
        })

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)