from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api_accounts.models import User
from api_accounts.serializers import UserRegistrationSerializer


class UserRegistrationView(CreateAPIView):
    """
    An endpoint for creating user.
    """

    queryset = User.objects.none()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        # Errors are handled inside serializer
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # TODO: add mailing service here
        return Response(
            {"message": f"Registration successful, check your email adress: {user.email}"},
            status=status.HTTP_201_CREATED,
        )
