from rest_framework import serializers
from .models import User

class UserSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    employee_id = serializers.CharField(required=False, allow_null=True)
    
    def create(self, validated_data):
        # Explicitly not supported here, handled in views manually
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
