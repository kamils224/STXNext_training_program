from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from smtplib import SMTPException

from api_accounts.models import User
from api_accounts.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ActivateAccountSerializer,
)
from api_accounts.utils import send_verification_email


class UserRegistrationView(CreateAPIView):
    """
    An endpoint for creating user.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        try:
            send_verification_email(
                user,
                request,
                subject="Training course",
                message="Hello! Activate your account here:\n",
            )
        except (SMTPException):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": f"Registration successful, check your email: {user}"},
            status=status.HTTP_201_CREATED,
        )


class UserDetailsView(RetrieveAPIView):
    """
    An endpoint for user details.
    Returns data based on the currently logged user, without providing his id/pk in URL.
    """

    serializer_class = UserSerializer

    def get_object(self):
        serializer = UserSerializer(self.request.user)
        return serializer.data


class ActivateAccountView(RetrieveAPIView):

    serializer_class = ActivateAccountSerializer
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        serializer = ActivateAccountSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {"message": "Email successfully verified!"}, status=status.HTTP_200_OK
        )
