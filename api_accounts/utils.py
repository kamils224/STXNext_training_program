from typing import Optional

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.request import Request
from rest_framework.reverse import reverse
from smtplib import SMTPException

__all__ = ["VerificationTokenGenerator", "send_verification_email"]


User = get_user_model()


class VerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


def send_verification_email(
    user: User,
    request: Request,
    subject: str = "Verify your email",
    message: str = "",
    sender: Optional[str] = None,
) -> None:
    token_generator = VerificationTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    message += _create_activation_url(uid, token, request)
    # The sender is set in DEFAULT_FROM_EMAIL in settings.py
    send_mail(subject, message, None, recipient_list=[user.email], fail_silently=False)


def _create_activation_url(uid: str, token: str, request: Request) -> str:
    endpoint = reverse("api_accounts:activate")
    protocol = "https" if request.is_secure() else "http"
    host = request.get_host()

    return f"{protocol}://{host}{endpoint}?uid={uid}&token={token}"
