from __future__ import annotations

import random

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now


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
            **extra_fields,
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
        editable=False,
        help_text='Unique key for internal operations',
    )
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
    is_new = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    created_on = models.DateField(default=now, editable=False)

    class Meta:
        unique_together = ['to_user', 'from_user']

    def __repr__(self) -> str:
        """Representation of a FriendRequest object"""

        return f'<FriendRequest: to {self.to_user} from {self.from_user}>'


class Friend(models.Model):
    """A model for User's friends"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )
    users_nickname = models.CharField(max_length=255, null=True, default=None)
    friend_of = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='friend_of'
    )
    start_date = models.DateField(default=now, editable=False)
    is_blocked = models.BooleanField(default=False)

    def __repr__(self):
        """Representation of a Friend object"""

        return f'<Friend: {self.user}, friend of {self.friend_of}>'
