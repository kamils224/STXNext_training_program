from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.request import Request
from smtplib import SMTPException
from django.core.mail import send_mail
from celery import shared_task

from api_accounts.utils import VerificationTokenGenerator, create_activation_url

User = get_user_model()


@shared_task
def send_verification_email(user: User, request: Request,
                            subject: str = "Verify your email", message: str = "") -> None:
    token_generator = VerificationTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    message += create_activation_url(uid, token, request)

    # The sender is set in DEFAULT_FROM_EMAIL in settings.py
    send_mail(subject, message, None, recipient_list=[
              user.email], fail_silently=False)
