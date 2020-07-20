from typing import Dict

from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    def create(self, validated_data: Dict) -> User:
        """Creates a new User"""

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: Dict) -> User:
        """Updates User's password"""

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
