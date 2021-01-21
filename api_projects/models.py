from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from stx_training_program.celery import app

from api_projects.tasks import send_issue_notification, notify_issue_deadline

User = get_user_model()


class Project(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, related_name="own_projects", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name="projects", blank=True)

    def __str__(self):
        return self.name


class Issue(models.Model):
    def __init__(self, *args, **kwargs):
        super(Issue, self).__init__(*args, **kwargs)
        # save these values before update
        self._original_due_date = self.due_date
        self._original_assigne = self.assigne

    class Status(models.TextChoices):
        TODO = "todo"
        IN_PROGRESS = "in progress"
        REVIEW = "review"
        DONE = "done"

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TODO
    )
    owner = models.ForeignKey(
        User, related_name="created_issues", on_delete=models.CASCADE
    )
    assigne = models.ForeignKey(
        User,
        related_name="own_issues",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Project, related_name="issues", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Issue, self).save(*args, **kwargs)

        if self._original_assigne != self.assigne:
            self._perform_assigne_notification()

        if self._original_due_date != self.due_date:
            self._perform_deadline_notification()

    def _perform_assigne_notification(self) -> str:
        if self.assigne is not None:
            send_issue_notification.delay(
                self.assigne.email,
                "New assignment",
                f"You are assigned to the task {self.title}",
            )

        if self._original_assigne is not None:
            send_issue_notification.delay(
                self.assigne.email,
                "Assigment is removed",
                f"You were removed from task {self.title}",
            )

    def _perform_deadline_notification(self):
        if self.assigne:
            current_task, _ = DateUpdateTask.objects.get_or_create(issue=self)
            if current_task.task_id is not None:
                # remove previous task due to date change
                app.control.revoke(
                    task_id=current_task.task_id, terminate=True)

            subject = "Your task is not completed!"
            message = f"The time for the task {self.title} is over :("
            current_task.task_id = notify_issue_deadline.s(
                self.pk, self.assigne.email, subject, message
            ).apply_async(eta=self.due_date)
            current_task.save()


# Can be extended / changed as more tasks are needed
class DateUpdateTask(models.Model):
    issue = models.OneToOneField(
        Issue, on_delete=models.CASCADE, primary_key=True, related_name="issue_task"
    )
    task_id = models.CharField(max_length=50, unique=True, blank=True)


# Note: custom fields in Issue init causes infinite loop during cascade deletion
# Empty pre_delete signal fixes this issue...
# source: https://code.djangoproject.com/ticket/31475
@receiver(pre_delete, sender=Issue)
def clean_custom_fields(sender, instance, **kwargs):
    pass
