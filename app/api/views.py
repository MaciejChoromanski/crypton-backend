from typing import Dict

from django.db.models.query import QuerySet
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.serializers import (
    UserSerializer,
    FriendRequestSerializer,
    FriendSerializer,
)

from core.models import User, FriendRequest, Friend


def friend_request_existence(first_user_pk: int, second_user_pk: int) -> Dict:
    """Checks if FriendRequest already exists"""

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

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating and deleting User's data"""

    serializer_class = UserSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> User:
        """Returns a current User"""

        return self.request.user


class CreateFriendRequestView(CreateAPIView):
    """Endpoint for creating new FriendRequest"""

    serializer_class = FriendRequestSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer) -> None:
        """
        Saves FriendRequest if 'crypto_key' was
        provided and FriendRequest doesn't exist
        """

        data = self.request.data.copy()
        crypto_key = data.get('crypto_key')
        if not crypto_key:
            raise ValidationError(detail='No \'crypto_key\' provided')
        user = get_object_or_404(User, crypto_key=crypto_key)
        friend_request = friend_request_existence(
            int(data['from_user']), user.pk
        )
        if friend_request['sent_by']:
            raise ValidationError(
                detail='You have already sent a FriendRequest to this User'
            )
        elif friend_request['sent_to']:
            raise ValidationError(
                detail='This User has already sent you a FriendRequest'
            )
        serializer.save(to_user=user)


class ListFriendRequestView(ListAPIView):
    """Endpoint for listing FriendRequest"""

    serializer_class = FriendRequestSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        """Returns QuerySet of FriendRequests sent to the User"""

        return FriendRequest.objects.filter(to_user=self.request.user)


class ManageFriendRequestView(RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating and deleting FriendRequest's data"""

    serializer_class = FriendRequestSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> FriendRequest:
        """Returns a FriendRequest if it was meant for the logged in User"""

        friend_request = get_object_or_404(FriendRequest, pk=self.kwargs['pk'])
        if self.request.user != friend_request.to_user:
            message = 'You don\'t have permission to manage this FriendRequest'
            raise PermissionDenied({'message': message})

        return friend_request


class CreateFriendView(CreateAPIView):
    """Endpoint for adding a new Friend"""

    serializer_class = FriendSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer) -> None:
        """Creates a new Friend if a FriendRequest exists and is accepted"""

        data = self.request.data
        friend_request = friend_request_existence(
            int(data['friend_of']), int(data['user'])
        ).get('instance')
        if not friend_request:
            raise ValidationError(
                detail='Can\'t create a Friend without a FriendRequest'
            )
        elif friend_request and not friend_request.is_accepted:
            raise ValidationError(
                detail='FriendRequest must be accepted to create a Friend'
            )
        serializer.save()
