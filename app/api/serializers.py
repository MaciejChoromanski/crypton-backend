from typing import Dict

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
)

from core.models import User, FriendRequest, Friend


class UserSerializer(ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username', 'crypto_key')
        read_only_fields = ('is_active', 'is_staff')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data: Dict) -> User:
        """Creates a new User"""

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: Dict) -> User:
        """Updates User's data"""

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class FriendRequestSerializer(ModelSerializer):
    """Serializer for the FriendRequest model"""

    class Meta:
        model = FriendRequest
        fields = ('from_user', 'to_user', 'is_new', 'is_accepted')


class FriendSerializer(ModelSerializer):
    """Serializer for the Friend model"""

    class Meta:
        model = Friend
        fields = ('user', 'users_nickname', 'friend_of', 'is_blocked')


class AuthTokenSerializer(Serializer):
    """Serializer for the authentication token"""

    email = CharField()
    password = CharField(
        style={'input_type': 'password'}, trim_whitespace=False
    )

    def validate(self, attrs: Dict) -> Dict:
        """Returns validated attributes"""

        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            message = _('Unable to authenticate with provided credentials')
            raise ValidationError(message, code='authentication')

        attrs['user'] = user

        return attrs
