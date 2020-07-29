from typing import Dict, Union

from django.db.models.query import QuerySet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny

from api import serializers

from core.models import User, FriendRequest, Friend
from rest_framework.settings import api_settings


def friend_request_info(
    first_user_pk: Union[int, str], second_user_pk: Union[int, str]
) -> Dict:
    """Returns info about the FriendRequest"""

    friend_request_sent_by_user = FriendRequest.objects.filter(
        to_user=second_user_pk, from_user=first_user_pk
    )
    friend_request_sent_to_user = FriendRequest.objects.filter(
        to_user=first_user_pk, from_user=second_user_pk
    )

    if friend_request_sent_by_user:
        friend_request = friend_request_sent_by_user[0]
    elif friend_request_sent_to_user:
        friend_request = friend_request_sent_to_user[0]
    else:
        friend_request = None

    return {
        'sent_by': friend_request_sent_by_user.exists(),
        'sent_to': friend_request_sent_to_user.exists(),
        'instance': friend_request,
    }


class CreateUserView(CreateAPIView):
    """Endpoint for creating new Users"""

    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating and deleting User's data"""

    serializer_class = serializers.UserSerializer

    def get_object(self) -> User:
        """Returns a current User"""

        return self.request.user


class CreateFriendRequestView(CreateAPIView):
    """Endpoint for creating new FriendRequest"""

    serializer_class = serializers.FriendRequestSerializer

    def get_serializer(self, *args, **kwargs) -> None:
        """
        Returns serializer class after checking if 'crypto_key' was
        provided and similar FriendRequest doesn't exist
        """

        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        data = self.request.data.copy()
        crypto_key = data.get('crypto_key')

        if not crypto_key:
            raise ValidationError(detail='No \'crypto_key\' provided')

        user = get_object_or_404(User, crypto_key=crypto_key)
        data['to_user'] = user.pk
        friend_request = friend_request_info(data['from_user'], user.pk)

        if friend_request['sent_by']:
            detail = 'You have already sent a FriendRequest to this User'
            raise ValidationError(detail=detail)
        elif friend_request['sent_to']:
            detail = 'This User has already sent you a FriendRequest'
            raise ValidationError(detail=detail)

        kwargs['data'] = data

        return serializer_class(*args, **kwargs)


class ListFriendRequestView(ListAPIView):
    """Endpoint for listing FriendRequest"""

    serializer_class = serializers.FriendRequestSerializer

    def get_queryset(self) -> QuerySet:
        """Returns QuerySet of FriendRequests sent to the User"""

        return FriendRequest.objects.filter(to_user=self.request.user)


class ManageFriendRequestView(RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating and deleting FriendRequest's data"""

    serializer_class = serializers.FriendRequestSerializer

    def get_object(self) -> FriendRequest:
        """Returns a FriendRequest if it was meant for the logged in User"""

        friend_request = get_object_or_404(FriendRequest, pk=self.kwargs['pk'])

        if self.request.user != friend_request.to_user:
            message = 'You don\'t have permission to manage this FriendRequest'
            raise PermissionDenied({'message': message})

        return friend_request


class CreateFriendView(CreateAPIView):
    """Endpoint for adding a new Friend"""

    serializer_class = serializers.FriendSerializer

    def perform_create(self, serializer) -> None:
        """Creates a new Friend if a FriendRequest exists and is accepted"""

        data = self.request.data
        friend_request = friend_request_info(
            data['friend_of'], data['user']
        ).get('instance')

        if not friend_request:
            detail = 'Can\'t create a Friend without a FriendRequest'
            raise ValidationError(detail=detail)
        elif friend_request and not friend_request.is_accepted:
            detail = 'FriendRequest must be accepted to create a Friend'
            raise ValidationError(detail=detail)

        serializer.save()


class ListFriendView(ListAPIView):
    """Endpoint for listing Friend"""

    serializer_class = serializers.FriendSerializer

    def get_queryset(self) -> QuerySet:
        """Returns a QueryFriends of User's friends"""

        return Friend.objects.filter(friend_of=self.request.user)


class ManageFriendView(RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating and deleting Friend's data"""

    serializer_class = serializers.FriendSerializer

    def get_object(self) -> Friend:
        """Returns a FriendRequest if it was meant for the logged in User"""

        friend = get_object_or_404(Friend, pk=self.kwargs['pk'])

        if self.request.user != friend.friend_of:
            message = 'You don\'t have permission to manage this Friend'
            raise PermissionDenied({'message': message})

        return friend


class CreateTokenView(ObtainAuthToken):
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
