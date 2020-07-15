from django.test import TestCase
from django.contrib.auth import get_user_model


def sample_user(email='test@testdomain.com', password='test_password'):
    return get_user_model().objects.create_user(email, password)


class TestUser(TestCase):
    """Tests for the User model"""

    def test_create_user_with_email_successful(self):
        username = 'test_username'
        email = 'test@testdomain.com'
        password = 'test_password'
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'test@TESTDOMAIN.com'
        user = get_user_model().objects.create_user(
            username='test_username',
            email=email,
            password='test_password'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username='test_username',
                email=None,
                password='test_password'
            )

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            username='test_username',
            email='test@testdomain.com',
            password='test_password'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
