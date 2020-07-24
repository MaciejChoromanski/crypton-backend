from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .utils import create_user, create_friend_request

from core.models import FriendRequest

CREATE_FRIEND_REQUEST_URL = reverse('api:friend_request_create')
LIST_FRIEND_REQUEST_URL = reverse('api:friend_request_list')
MANAGE_FRIEND_REQUEST_URL = 'api:friend_request_manage'


class TestPublicFriendRequestAPI(TestCase):
    """Tests for the public API for the FriendRequest model"""

    def setUp(self) -> None:
        """Sets up the APIClient for the tests"""

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

    def test_create_friend_request_unauthorized(self) -> None:
        """
        Tests what happens if a FriendRequest is created by an anonymous User
        """

        payload = {'to_user': self.user_one, 'from_user': self.user_two}
        response = self.client.post(CREATE_FRIEND_REQUEST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_friend_request_unauthorized(self) -> None:
        """
        Tests what happens if a FriendRequest is listed by an anonymous User
        """

        payload = {'to_user': self.user_one, 'from_user': self.user_two}
        create_friend_request(**payload)
        response = self.client.get(LIST_FRIEND_REQUEST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manage_friend_request_unauthorized(self) -> None:
        """
        Tests what happens if a FriendRequest is managed by an anonymous User
        """

        payload = {'to_user': self.user_one, 'from_user': self.user_two}
        friend_request = FriendRequest.objects.create(**payload)
        response = self.client.get(
            reverse(
                MANAGE_FRIEND_REQUEST_URL, kwargs={'pk': friend_request.pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestFriendRequestPrivateAPI(TestCase):
    """Tests for the private API for the FriendRequest model"""

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

    def test_create_friend_request_successfully(self) -> None:
        """Tests if a FriendRequest is created successfully"""

        payload = {'to_user': self.user_two.pk, 'from_user': self.user_one.pk}
        response = self.client.post(CREATE_FRIEND_REQUEST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_friend_request_already_exists(self) -> None:
        """
        Tests if a FriendRequest is created when the same one already exists
        """

        payload = {'to_user': self.user_two, 'from_user': self.user_one}
        create_friend_request(**payload)
        payload.update(to_user=self.user_two.pk, from_user=self.user_one.pk)
        response = self.client.post(CREATE_FRIEND_REQUEST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_friend_request_successfully(self) -> None:
        """Tests if a FriendRequest is listed successfully"""

        payload = {'to_user': self.user_two, 'from_user': self.user_one}
        create_friend_request(**payload)
        response = self.client.get(LIST_FRIEND_REQUEST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manage_friend_request_does_not_exist(self) -> None:
        """
        Tests what happens when User tries to
        access FriendRequest, which doesn't exist
        """

        response = self.client.get(
            reverse(MANAGE_FRIEND_REQUEST_URL, kwargs={'pk': 1})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_friend_request_successfully(self) -> None:
        """Tests if a FriendRequest is retrieved successfully"""

        payload = {'to_user': self.user_two, 'from_user': self.user_one}
        friend_request = FriendRequest.objects.create(**payload)
        response = self.client.get(
            reverse(
                MANAGE_FRIEND_REQUEST_URL, kwargs={'pk': friend_request.pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_friend_request_successfully(self) -> None:
        """Tests if a FriendRequest is updated successfully"""

        payload = {'to_user': self.user_two, 'from_user': self.user_one}
        friend_request = FriendRequest.objects.create(**payload)
        response = self.client.patch(
            reverse(
                MANAGE_FRIEND_REQUEST_URL, kwargs={'pk': friend_request.pk}
            ),
            {'is_new': False},
        )
        friend_request.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(friend_request.is_new)

    def test_delete_friend_request_successfully(self) -> None:
        """Tests if a FriendRequest is deleted successfully"""

        payload = {'to_user': self.user_two, 'from_user': self.user_one}
        friend_request = FriendRequest.objects.create(**payload)
        response = self.client.delete(
            reverse(
                MANAGE_FRIEND_REQUEST_URL, kwargs={'pk': friend_request.pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            FriendRequest.objects.filter(pk=friend_request.pk).exists()
        )
