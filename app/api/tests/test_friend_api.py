from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .utils import create_user, create_friend_request, create_friend

from core.models import Friend

CREATE_FRIEND_URL = reverse('api:friend_create')
LIST_FRIEND_URL = reverse('api:friend_list')


class TestPublicFriendAPI(TestCase):
    """Tests for the public API for the Friend model"""

    def setUp(self) -> None:
        """Creates client and users for the tests"""

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

    def test_create_friend_unauthorized(self) -> None:
        """
        Tests what happens if a Friend is created by an anonymous User
        """

        data = {
            'to_user': self.user_one,
            'from_user': self.user_two,
            'is_accepted': True,
        }
        create_friend_request(**data)
        payload = {'user': self.user_two, 'friend_of': self.user_two}
        response = self.client.post(CREATE_FRIEND_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_friend_unauthorized(self) -> None:
        """Tests what happens if an anonymous User tries to list Friends"""

        response = self.client.get(LIST_FRIEND_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateFriendAPI(TestCase):
    """Tests for the private API for the Friend model"""

    def setUp(self) -> None:
        """Creates client and users for the tests"""

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

    def test_create_friend_successfully(self) -> None:
        """Tests if a Friend is created successfully"""

        data = {
            'to_user': self.user_one,
            'from_user': self.user_two,
            'is_accepted': True,
        }
        create_friend_request(**data)
        payload = {'user': self.user_two.pk, 'friend_of': self.user_one.pk}
        response = self.client.post(CREATE_FRIEND_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_friend_not_accepted_friend_request(self) -> None:
        """
        Tests if a Friend is not created when
        the FriendRequest hasn't been accepted
        """

        data = {
            'to_user': self.user_one,
            'from_user': self.user_two,
        }
        create_friend_request(**data)
        payload = {'user': self.user_two.pk, 'friend_of': self.user_one.pk}
        response = self.client.post(CREATE_FRIEND_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            b'FriendRequest must be accepted to create a Friend',
            response.content
        )

    def test_create_friend_not_sent_friend_request(self) -> None:
        """
        Tests if a Friend is not created when
        the FriendRequest hasn't been created
        """

        payload = {'user': self.user_two.pk, 'friend_of': self.user_one.pk}
        response = self.client.post(CREATE_FRIEND_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            b'Can\'t create a Friend without a FriendRequest', response.content
        )

    def test_list_friend_successfully(self) -> None:
        """Tests if a Friend is listed successfully"""

        data = {'user': self.user_two, 'friend_of': self.user_one}
        create_friend(**data)
        response = self.client.get(LIST_FRIEND_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
