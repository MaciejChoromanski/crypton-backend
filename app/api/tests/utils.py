from typing import Union

from django.contrib.auth import get_user_model

from core.models import User, FriendRequest, Friend, Message


def create_user(**params: str) -> User:
    """Creates a User with a given params"""

    return get_user_model().objects.create_user(**params)


def create_friend_request(**params: User) -> FriendRequest:
    """Creates a FriendRequest with a given params"""

    return FriendRequest.objects.create(**params)


def create_friend(**params: User) -> Friend:
    """Creates a Friend with a given params"""

    return Friend.objects.create(**params)


def create_message(**params: Union[str, User]) -> Message:
    """Creates a Message with a given params"""

    return Message.objects.create(**params)
