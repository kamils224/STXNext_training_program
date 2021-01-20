from django.core.validators import MinLengthValidator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from api_accounts.models import User
from api_accounts.utils import VerificationTokenGenerator


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(validators=[MinLengthValidator(8)])

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


class ActivateAccountSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data) -> User:
        """
        Overloaded validation checks if uid and token are correct and returns corresponding User object.
        """
        uid = data["uid"]
        token = data["token"]
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (ObjectDoesNotExist, ValueError):
            raise serializers.ValidationError("Given user does not exist")

        activation_token = VerificationTokenGenerator()
        if not activation_token.check_token(user, token):
            raise serializers.ValidationError("Given token is wrong")
        return user
