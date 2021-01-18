from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.reverse import reverse


__all__ = ["VerificationTokenGenerator", "create_activation_url"]


User = get_user_model()


class VerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


def create_activation_url(uid: str, token: str, request: Request) -> str:
    endpoint = reverse("api_accounts:activate")
    protocol = "https" if request.is_secure() else "http"
    host = request.get_host()

    return f"{protocol}://{host}{endpoint}?uid={uid}&token={token}"
