from typing import List

from django.core.mail import send_mail


# Note: class will be extended along with incoming features
class BaseMailer():
    def send_email(self, subject: str, message: str,
                   from_email: str, to_email: List[str]) -> None:
        send_mail(subject, message, from_email, to_email, fail_silently=False)
