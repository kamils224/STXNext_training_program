from rest_framework import serializers

from api_accounts.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {"password": {"required": True, "write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["email"], validated_data["password"]
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]
