from rest_framework import generics, permissions

from api.serializers import UserSerializer

from core.models import User


class CreateUserView(generics.CreateAPIView):
    """Endpoint for creating new Users"""

    serializer_class = UserSerializer
    queryset = User.objects.all()


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating and deleting User's data"""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> User:
        """Returns a User"""

        return self.request.user
