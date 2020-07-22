from __future__ import annotations

import random
from typing import List

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
        self, username: str, email: str, password: str, **extra_fields
    ) -> User:
        """Creates a user with a given username, email and password"""

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            crypto_key=self._generate_crypto_key(),
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self, username: str, email: str, password: str
    ) -> User:
        """Creates a superuser with a given username, email and password"""

        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def _generate_crypto_key(self) -> int:
        """Generates crypto_key for a user"""

        key = random.randint(100000000, 999999999)
        if self.filter(crypto_key=key).exists():
            self._generate_crypto_key()

        return key


class User(AbstractBaseUser, PermissionsMixin):
    """A model for app's Users"""

    crypto_key = models.IntegerField(
        unique=True,
        validators=[
            MinValueValidator(1000000000),
            MaxValueValidator(999999999),
        ],
        help_text='Unique key for internal operations',
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    friends = models.ManyToManyField('self')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def friends_list(self) -> List:
        """Returns a list of friends"""

        return list(self.friends.all())

    def __str__(self) -> str:
        """Returns User's username"""

        return f'{self.username}'

    def __repr__(self) -> str:
        """Representation of a User object"""

        return f'<User: {self.username}>'


class FriendRequest(models.Model):
    """A model for friend's requests from one User to another"""

    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='to_user'
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='from_user'
    )

    def __repr__(self) -> str:
        """Representation of a FriendRequest object"""

        return f'<FriendRequest: to {self.to_user} from {self.from_user}>'
