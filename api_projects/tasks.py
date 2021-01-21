from celery import shared_task

from django.apps import apps
from django.core.mail import send_mail


@shared_task
def send_issue_notification(email: str, subject: str, message: str) -> None:
    send_mail(subject, message, None, recipient_list=[
              email], fail_silently=False)


@shared_task
def notify_issue_deadline(pk: int, email: str, subject: str, message: str) -> None:
    # to prevent circular imports
    from api_projects.models import Issue

    issue = Issue.objects.get(pk=pk)
    if issue.status != issue.Status.DONE and issue.assigne is not None:
        send_issue_notification(
            email,
            "Issue deadline",
            f"The {issue.title} is not finished after deadline!",
        )
        issue.issue_task.delete()
