from datetime import datetime

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import FriendRequest, Friend, Message


class TestUser(TestCase):
    """Tests for the User model"""

    def test_create_user_with_email_successful(self) -> None:
        """Tests if User is created successfully"""

        username = 'test_username'
        email = 'test@testdomain.com'
        password = 'test_password'
        user = get_user_model().objects.create_user(
            username=username, email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.username, username)

    def test_new_user_email_normalized(self) -> None:
        """Tests if User's email is normalized"""

        email = 'test@TESTDOMAIN.com'
        user = get_user_model().objects.create_user(
            username='test_username', email=email, password='test_password'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self) -> None:
        """Tests if Users is created when the email is invalid"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username='test_username', email=None, password='test_password'
            )

    def test_create_new_superuser(self) -> None:
        """Tests if superuser is created successfully"""

        user = get_user_model().objects.create_superuser(
            username='test_username',
            email='test@testdomain.com',
            password='test_password',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class TestFriendRequest(TestCase):
    """Tests for the FriendRequest model"""

    def setUp(self) -> None:
        """Creates Users for tests purposes"""

        self.user_one = get_user_model().objects.create_user(
            username='user_one',
            email='user_one@testdomain.com',
            password='password_one',
        )
        self.user_two = get_user_model().objects.create_user(
            username='user_two',
            email='user_two@testdomain.com',
            password='password_two',
        )

    def test_create_friend_request_successful(self) -> None:
        """Tests if FriendRequest is created successfully"""

        friends_request = FriendRequest.objects.create(
            to_user=self.user_one, from_user=self.user_two
        )

        self.assertEqual(friends_request.to_user, self.user_one)
        self.assertEqual(friends_request.from_user, self.user_two)
        self.assertTrue(friends_request.is_new)
        self.assertFalse(friends_request.is_accepted)
        self.assertIsInstance(friends_request.created_on, datetime)

    def test_friend_request_unique_constraint(self) -> None:
        """
        Tests if FriendRequest isn't created when
        there's already one with the same Users
        """

        FriendRequest.objects.create(
            to_user=self.user_one, from_user=self.user_two
        )
        with self.assertRaises(IntegrityError):
            FriendRequest.objects.create(
                to_user=self.user_one, from_user=self.user_two
            )

    def test_friend_request_custom_validation(self) -> None:
        """
        Tests if FriendRequest isn't created when there's already
        one with the same Users but in different fields
        """

        FriendRequest.objects.create(
            to_user=self.user_one, from_user=self.user_two
        )
        with self.assertRaises(ValidationError):
            FriendRequest.objects.create(
                to_user=self.user_two, from_user=self.user_one
            )


class TestFriend(TestCase):
    """Tests for the Friend model"""

    def test_create_friend_successful(self) -> None:
        """Tests if Friend is created successfully"""

        user_one = get_user_model().objects.create_user(
            username='user_one',
            email='user_one@testdomain.com',
            password='password_one',
        )
        user_two = get_user_model().objects.create_user(
            username='user_two',
            email='user_two@testdomain.com',
            password='password_two',
        )
        friend = Friend.objects.create(user=user_two, friend_of=user_one)

        self.assertEqual(friend.user, user_two)
        self.assertIsNone(friend.users_nickname)
        self.assertEqual(friend.friend_of, user_one)
        self.assertIsInstance(friend.start_date, datetime)
        self.assertFalse(friend.is_blocked)


class TestMessage(TestCase):
    """Tests for the Message model"""

    def setUp(self) -> None:
        """Creates Users for the test purposes"""

        self.user_one = get_user_model().objects.create_user(
            username='user_one',
            email='user_one@testdomain.com',
            password='password_one',
        )
        self.user_two = get_user_model().objects.create_user(
            username='user_two',
            email='user_two@testdomain.com',
            password='password_two',
        )

    def test_create_message_successful(self) -> None:
        """Tests if Message is created successfully"""

        Friend.objects.create(user=self.user_two, friend_of=self.user_one)
        message = Message.objects.create(
            content='text', to_user=self.user_two, from_user=self.user_one
        )

        self.assertEqual(message.content, 'text')
        self.assertEqual(message.to_user, self.user_two)
        self.assertEqual(message.from_user, self.user_one)
        self.assertTrue(message.is_new)
        self.assertIsInstance(message.sent_on, datetime)

    def test_create_message_users_are_not_friends(self) -> None:
        """Tests if Message is created successfully"""

        with self.assertRaises(ValidationError):
            Message.objects.create(
                content='text', to_user=self.user_two, from_user=self.user_one
            )
