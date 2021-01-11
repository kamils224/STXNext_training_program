from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


from api_accounts.models import User
from api_accounts.serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    An endpoint for creating user.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                # TODO: add email message with verification url
                return Response(
                    {"message": "Registration successful, check your email!"},
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)