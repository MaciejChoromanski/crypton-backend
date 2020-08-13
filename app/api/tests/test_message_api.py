from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .utils import create_user

from core.models import Message, Friend

CREATE_MESSAGE_URL = reverse('api:message_create')


class TestPublicMessageAPI(TestCase):
    """Tests for the public API for the Message model"""

    def setUp(self) -> None:
        """Sets up the APIClient for the tests and creates users"""

        self.user_one = create_user(
            email='one@testdomain.com',
            password='test_password_one',
            username='test_username_one',
        )
        self.user_two = create_user(
            email='two@testdomain.com',
            password='test_password_two',
            username='test_username_two',
        )
        self.client = APIClient()

    def test_create_message_unauthorized(self) -> None:
        """
        Tests what happens if a Message is created by an anonymous User
        """

        payload = {
            'content': 'text',
            'to_user': self.user_one,
            'from_user': self.user_two,
        }
        response = self.client.post(CREATE_MESSAGE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateMessageAPI(TestCase):
    """Tests for the private API for the Message model"""

    def setUp(self) -> None:
        """Sets up the APIClient for the tests and creates users"""

        self.user_one = create_user(
            email='one@testdomain.com',
            password='test_password_one',
            username='test_username_one',
        )
        self.user_two = create_user(
            email='two@testdomain.com',
            password='test_password_two',
            username='test_username_two',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user_one)

    def test_create_message_successfully(self) -> None:
        """Tests if Message is created successfully"""

        Friend.objects.create(user=self.user_two, friend_of=self.user_one)
        payload = {
            'content': 'text',
            'to_user': self.user_one.pk,
            'from_user': self.user_two.pk,
        }
        response = self.client.post(CREATE_MESSAGE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_message_users_are_not_friends(self) -> None:
        """Tests if Message is created successfully"""

        payload = {
            'content': 'text',
            'to_user': self.user_one,
            'from_user': self.user_two,
        }
        response = self.client.post(CREATE_MESSAGE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
