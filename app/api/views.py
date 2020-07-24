from django.db.models.query import QuerySet
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated

from api.serializers import UserSerializer, FriendRequestSerializer

from core.models import User, FriendRequest


class CreateUserView(CreateAPIView):
    """Endpoint for creating new Users"""

    serializer_class = UserSerializer
    queryset = User.objects.all()


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
        """Returns a FriendRequest"""

        return get_object_or_404(FriendRequest, pk=self.kwargs['pk'])
