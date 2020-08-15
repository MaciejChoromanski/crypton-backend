from __future__ import annotations

import random
from typing import Any, Dict, Union

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now


class UserManager(BaseUserManager):
    """Manager for the User model"""

    def create_user(
        self, username: str, email: str, password: str, **extra_fields: Any
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


class FriendRequestManager(models.Manager):
    """Manager for the Friend model"""

    def create(self, *args: Any, **kwargs: Any) -> FriendRequest:
        """Creates FriendRequest if conditions are met"""

        self._validate_friend_request_existence(**kwargs)

        return super().create(*args, **kwargs)

    def get_or_none(self, **kwargs: Any) -> Union[FriendRequest, None]:
        """Returns FriendsRequest if it was sent to one of the Users or None"""

        first_user = kwargs['from_user']
        second_user = kwargs['to_user']
        sent_friend_request = self.filter(
            to_user=second_user, from_user=first_user
        )

        if sent_friend_request:
            return sent_friend_request[0]

        received_friend_request = self.filter(
            to_user=first_user, from_user=second_user
        )

        if received_friend_request:
            return received_friend_request[0]

        return None

    def _validate_friend_request_existence(self, **kwargs: Any) -> None:
        """Validates if similar FriendRequest already exists"""

        friend_request = self.get_or_none(**kwargs)

        if friend_request:
            raise ValidationError('Similar FriendRequest already exists')


class FriendRequest(models.Model):
    """A model for friend's requests from one User to another"""

    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='to_user_friend_request'
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='from_user_friend_request'
    )
    is_new = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    created_on = models.DateField(default=now, editable=False)

    objects = FriendRequestManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['to_user', 'from_user'], name='uq_users'
            )
        ]

    def __repr__(self) -> str:
        """Representation of a FriendRequest object"""

        return f'<FriendRequest: to {self.to_user} from {self.from_user}>'


class FriendManager(models.Manager):
    """Manager for the Friend model"""

    def create(self, *args: Any, **kwargs: Any) -> Friend:
        """Creates Friend if conditions are met"""

        self._validate_friend_request(**kwargs)

        return super().create(*args, **kwargs)

    @staticmethod
    def are_friends(first_user: User, second_user: User) -> bool:
        """Checks if Users are friends"""

        users_are_friends = (
            Friend.objects.filter(
                user=first_user, friend_of=second_user
            ).exists()
            or
            Friend.objects.filter(
                user=second_user, friend_of=first_user
            ).exists()
        )

        return users_are_friends

    @staticmethod
    def _validate_friend_request(**kwargs: Any) -> None:
        """Validates if FriendRequest exists and is accepted"""

        from_user = kwargs['user']
        to_user = kwargs['friend_of']
        friend_request = FriendRequest.objects.get_or_none(
            from_user=from_user, to_user=to_user
        )

        if not friend_request:
            message = 'FriendRequest must exist to create a Friend'
            raise ValidationError(message)

        if not friend_request.is_accepted:
            message = 'FriendRequest must be accepted to create a Friend'
            raise ValidationError(message)


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

    objects = FriendManager()

    def __repr__(self) -> str:
        """Representation of a Friend object"""

        return f'<Friend: {self.user}, friend of {self.friend_of}>'


class MessageManager(models.Manager):
    """Manager for the Message model"""

    def create(self, *args: Any, **kwargs: Any) -> Friend:
        """Creates a Message if Users are friends"""

        self._validate_friendship(**kwargs)

        return super().create(*args, **kwargs)

    @staticmethod
    def _validate_friendship(**kwargs: Any) -> None:
        """Validates if Users are friends"""

        users_are_friends = Friend.objects.are_friends(
            kwargs['to_user'], kwargs['from_user']
        )

        if not users_are_friends:
            message = 'Message can\'t be created because Users aren\'t friends'
            raise ValidationError(message)


class Message(models.Model):
    """A model for messages, which Users sent to each other"""

    content = models.TextField()
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='to_user_message'
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='from_user_message'
    )
    is_new = models.BooleanField(default=True)
    sent_on = models.DateTimeField(default=now, editable=False)

    objects = MessageManager()

    def __repr__(self) -> str:
        """Representation of a Message object"""

        return f'<Message: to {self.to_user} from {self.from_user}>'
