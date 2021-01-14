from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view


from api_accounts.models import User
from api_accounts.serializers import UserRegistrationSerializer, UserSerializer
from api_accounts.utils import VerificationTokenGenerator, send_verification_email


class UserRegistrationView(CreateAPIView):
    """
    An endpoint for creating user.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user, request,
                                subject="Training course", message="Hello! Activate your account here:\n")
        return Response({"message": f"Registration successful, check your email: {user}"},
                        status=status.HTTP_201_CREATED)


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def activate_account(request):
    uid = request.query_params.get("uid")
    token = request.query_params.get("token")

    if uid is not None and token is not None:
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user is not None:
            activation_token = VerificationTokenGenerator()
            if not user.is_active and activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Email successfully verified!"},
                                status=status.HTTP_200_OK)

    return Response(status=status.HTTP_404_NOT_FOUND)
