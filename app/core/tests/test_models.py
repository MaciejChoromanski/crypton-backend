from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import FriendRequest


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
        self.assertEqual(user.friends_list, [])

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

    def test_create_friend_request_successful(self) -> None:
        """Tests if FriendRequest is created successfully"""

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
        friends_request = FriendRequest.objects.create(
            to_user=user_one, from_user=user_two
        )

        self.assertEqual(friends_request.to_user, user_one)
        self.assertEqual(friends_request.from_user, user_two)
        self.assertTrue(friends_request.is_new)
