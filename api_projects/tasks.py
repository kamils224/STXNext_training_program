from functools import wraps
from dataclasses import dataclass

from django.core.mail import send_mail
from celery import shared_task


@dataclass
class NotificationData:
    email: str
    subject: str
    message: str


@shared_task
def send_issue_notification(email: str, subject: str, message: str):
    send_mail(subject, message, None, recipient_list=[
              email], fail_silently=False)
