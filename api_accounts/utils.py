from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.request import Request
from rest_framework.reverse import reverse_lazy


__all__ = ["VerificationTokenGenerator", "send_verification_email"]


User = get_user_model()


class VerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


VERIFICATION_URL = reverse_lazy("api_accounts:activate")
ACTIVATION_SUBJECT = "Activate your account"
FROM_EMAIL = settings.FROM_EMAIL


def send_verification_email(user: User, request: Request) -> None:
    token_generator = VerificationTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    protocol = "https" if request.is_secure() else "http"
    host = request.get_host()

    activation_link = f"{protocol}://{host}{VERIFICATION_URL}?uid={uid}&token={token}"
    message = f"Hello {user.email}, please verify your email here:\n {activation_link}"
    send_mail(ACTIVATION_SUBJECT, message, FROM_EMAIL, [user.email])
