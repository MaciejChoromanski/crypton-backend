from __future__ import annotations

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserManager(BaseUserManager):
    """Manager for the User model"""

    def create_user(
            self, crypto_key: int, username: str,
            email: str, password: str, **extra_fields
    ) -> User:
        """Creates a user with a given email and a password"""

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            crypto_key=crypto_key, username=username,
            email=self.normalize_email(email), **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
            self, crypto_key: int, username: str, email: str, password: str
    ) -> User:
        """Creates a superuser with a given email and a password"""

        user = self.create_user(crypto_key, username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """A model for app's Users"""

    crypto_key = models.IntegerField(
        unique=True,
        validators=[
            MinValueValidator(1000000000), MaxValueValidator(999999999)
        ],
        help_text='Unique key for internal operations'
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
