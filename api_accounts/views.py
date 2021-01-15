from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


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
        success = send_verification_email(
            user,
            request,
            subject="Training course",
            message="Hello! Activate your account here:\n"
        )
        if not success:
            User.objects.delete(user)
            return Response({"error": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Registration successful, check your email: {user}"},
                        status=status.HTTP_201_CREATED)


class UserDetailsView(RetrieveAPIView):
    """
    An endpoint for user details. 
    Returns data based on the currently logged user, without providing his id/pk in URL.
    """

    serializer_class = UserSerializer

    def get_object(self):
        serializer = UserSerializer(self.request.user)
        return serializer.data


@api_view(['GET'])
@permission_classes([AllowAny])
def activate_account(request):
    """
    An endpoint for activating account. Verifies if given credentials match any user.
    """
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
