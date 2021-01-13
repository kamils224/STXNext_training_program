from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api_accounts.models import User
from api_accounts.serializers import UserRegistrationSerializer, UserSerializer


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
            {
                "message":
                f"Registration successful, check your email: {user.email}"
            },
            status=status.HTTP_201_CREATED
        )


class UserDetailsView(RetrieveAPIView):
    """
    An endpoint for user details. 
    Returns data based on the currently logged user, without providing his id/pk in URL.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        serializer = UserSerializer(self.request.user)
        return serializer.data
