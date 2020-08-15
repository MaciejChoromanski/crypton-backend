from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from rest_framework.test import APIClient
from rest_framework import status

from .utils import (
    create_user,
    create_friend_request,
    create_friend,
    create_message,
)

from core.models import Message, Friend, User

CREATE_MESSAGE_URL = reverse('api:message_create')
LIST_MESSAGE_URL = reverse('api:message_list')
MANAGE_MESSAGE_URL = 'api:message_manage'


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

    def test_list_message_unauthorized(self) -> None:
        """
        Tests what happens if a Message is listed by an anonymous User
        """

        response = self.client.get(CREATE_MESSAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manage_message_unauthorized(self) -> None:
        """
        Tests what happens if a Message is managed by an anonymous User
        """

        response = self.client.get(
            reverse(MANAGE_MESSAGE_URL, kwargs={'pk': 1})
        )

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

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
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

    def test_list_message_successful(self) -> None:
        """Tests if Message is listed successfully"""

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        first_message = create_message(
            content='first message',
            to_user=self.user_two,
            from_user=self.user_one,
        )
        second_message = create_message(
            content='second message',
            to_user=self.user_one,
            from_user=self.user_two,
        )
        data = {'friend_pk': self.user_two.pk}
        response = self.client.get(LIST_MESSAGE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], second_message.content)
        self.assertEqual(response.data[1]['content'], first_message.content)

    def test_list_message_no_friend_pk_provided(self) -> None:
        """
        Tests what happens when no friend_pk is
        provided when calling the list view
        """

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        create_message(
            content='message', to_user=self.user_two, from_user=self.user_one
        )
        response = self.client.get(LIST_MESSAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_message_friend_does_not_exist(self) -> None:
        """
        Tests what happens if User's friend doesn't exist
        """

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        create_message(
            content='message', to_user=self.user_two, from_user=self.user_one
        )
        User.objects.filter(pk=self.user_two.pk).delete()
        data = {'friend_pk': self.user_two.pk}
        response = self.client.get(LIST_MESSAGE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_message_users_are_not_friends(self) -> None:
        """
        Tests what happens if users aren't friends and the list view is called
        """

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        create_message(
            content='message', to_user=self.user_two, from_user=self.user_one
        )
        Friend.objects.filter(
            user=self.user_two, friend_of=self.user_one
        ).delete()
        data = {'friend_pk': self.user_two.pk}
        response = self.client.get(LIST_MESSAGE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_message_which_does_not_exist(self) -> None:
        """
        Tests what happens if a User tries to
        retrieve a Message which doesn't exist
        """

        response = self.client.get(
            reverse(MANAGE_MESSAGE_URL, kwargs={'pk': 1})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manage_message_forbidden(self) -> None:
        """
        Tests what happens if User's trying to
        manage Message not meant for them
        """

        user_three = create_user(
            email='three@testdomain.com',
            password='test_password_three',
            username='test_username_three',
        )
        create_friend_request(
            from_user=self.user_two, to_user=user_three, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=user_three)
        message = create_message(
            content='message', to_user=self.user_two, from_user=user_three
        )
        response = self.client.get(
            reverse(MANAGE_MESSAGE_URL, kwargs={'pk': message.pk})
        )
        error_message = b'You don\'t have permission to manage this Message'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(error_message, response.content)

    @freeze_time('2020-09-25 17:17:17')
    def test_retrieve_message_successful(self) -> None:
        """
        Tests what happens if a Message is retrieved successfully
        """

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        message = create_message(
            content='message', to_user=self.user_two, from_user=self.user_one
        )
        response = self.client.get(
            reverse(MANAGE_MESSAGE_URL, kwargs={'pk': message.pk})
        )
        expected_result = {
            'content': 'message',
            'to_user': self.user_two.pk,
            'from_user': self.user_one.pk,
            'is_new': True,
            'sent_on': '2020-09-25T17:17:17Z',
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_result)

    def test_update_message_successful(self) -> None:
        """Tests if a Message is updated successfully"""

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        message = create_message(
            content='message', to_user=self.user_two, from_user=self.user_one
        )
        payload = {'content': 'new message', 'is_new': False}
        response = self.client.patch(
            reverse(MANAGE_MESSAGE_URL, kwargs={'pk': message.pk}), payload
        )
        message.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(message.content, 'new message')
        self.assertFalse(message.is_new)

    def test_delete_message_successful(self) -> None:
        """Tests if a Message is deleted successfully"""

        create_friend_request(
            from_user=self.user_two, to_user=self.user_one, is_accepted=True
        )
        create_friend(user=self.user_two, friend_of=self.user_one)
        message = create_message(
            content='message', to_user=self.user_two, from_user=self.user_one
        )
        response = self.client.delete(
            reverse(MANAGE_MESSAGE_URL, kwargs={'pk': message.pk})
        )
        message_exists = Message.objects.filter(pk=message.pk).exists()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(message_exists)
