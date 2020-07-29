from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .utils import create_user, create_friend_request, create_friend

from core.models import Friend

CREATE_FRIEND_URL = reverse('api:friend_create')
LIST_FRIEND_URL = reverse('api:friend_list')
MANAGE_FRIEND_URL = 'api:friend_manage'


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

    def test_manage_friend_request_unauthorized(self) -> None:
        """
        Tests what happens if a FriendRequest is managed by an anonymous User
        """

        response = self.client.get(
            reverse(MANAGE_FRIEND_URL, kwargs={'pk': 1})
        )

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

        data = {'to_user': self.user_one, 'from_user': self.user_two}
        create_friend_request(**data)
        payload = {'user': self.user_two.pk, 'friend_of': self.user_one.pk}
        response = self.client.post(CREATE_FRIEND_URL, payload)
        message = b'FriendRequest must be accepted to create a Friend'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(message, response.content)

    def test_create_friend_not_sent_friend_request(self) -> None:
        """
        Tests if a Friend is not created when
        the FriendRequest hasn't been created
        """

        payload = {'user': self.user_two.pk, 'friend_of': self.user_one.pk}
        response = self.client.post(CREATE_FRIEND_URL, payload)
        message = b'Can\'t create a Friend without a FriendRequest'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(message, response.content)

    def test_list_friend_successfully(self) -> None:
        """Tests if a Friend is listed successfully"""

        data = {'user': self.user_two, 'friend_of': self.user_one}
        create_friend(**data)
        response = self.client.get(LIST_FRIEND_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_manage_friend_does_not_exist(self) -> None:
        """
        Tests what happens when User tries to
        access Friend, which doesn't exist
        """

        response = self.client.get(
            reverse(MANAGE_FRIEND_URL, kwargs={'pk': 1})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manage_friend_forbidden(self) -> None:
        """
        Tests what happens when User tries to
        access FriendRequest, which was't meant for them
        """

        data = {'user': self.user_one, 'friend_of': self.user_two}
        friend = create_friend(**data)
        response = self.client.get(
            reverse(MANAGE_FRIEND_URL, kwargs={'pk': friend.pk})
        )
        message = b'You don\'t have permission to manage this Friend'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(message, response.content)

    def test_retrieve_friend_successfully(self) -> None:
        """Tests if a Friend is retrieved successfully"""

        data = {'user': self.user_two, 'friend_of': self.user_one}
        friend = create_friend(**data)
        response = self.client.get(
            reverse(MANAGE_FRIEND_URL, kwargs={'pk': friend.pk})
        )
        expected_result = {
            'user': self.user_two.pk,
            'friend_of': self.user_one.pk,
            'users_nickname': None,
            'is_blocked': False,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_update_friend_successfully(self) -> None:
        """Tests if a Friend is updated successfully"""

        data = {'user': self.user_two, 'friend_of': self.user_one}
        friend = create_friend(**data)
        payload = {'users_nickname': 'nickname', 'is_blocked': True}
        response = self.client.patch(
            reverse(MANAGE_FRIEND_URL, kwargs={'pk': friend.pk}), payload
        )
        friend.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(friend.users_nickname, 'nickname')
        self.assertTrue(friend.is_blocked)

    def test_delete_friend_successfully(self) -> None:
        """Tests if a Friend is deleted successfully"""

        data = {'user': self.user_two, 'friend_of': self.user_one}
        friend = create_friend(**data)
        response = self.client.delete(
            reverse(MANAGE_FRIEND_URL, kwargs={'pk': friend.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Friend.objects.filter(pk=friend.pk).exists())
