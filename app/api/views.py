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
)

from core.models import User, FriendRequest


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
        friend_request_exists = FriendRequest.objects.filter(
            to_user=user.pk, from_user=data['from_user']
        ).exists()
        if friend_request_exists:
            raise ValidationError(detail='FriendRequest already exists')
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
