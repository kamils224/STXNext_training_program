from django.db import models
from django.db.models import F, Q
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from api_projects.tasks import send_issue_notification, NotificationData

User = get_user_model()


class Project(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, related_name="own_projects", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name="projects", blank=True)

    def __str__(self):
        return self.name


class Issue(models.Model):

    def __init__(self, *args, **kwargs):
        super(Issue, self).__init__(*args, **kwargs)
        # save these values before update
        self.__original_due_date = self.due_date
        self.__original_assigne = self.assigne

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
        max_length=20, choices=Status.choices, default=Status.TODO)
    owner = models.ForeignKey(
        User, related_name="created_issues", on_delete=models.CASCADE)
    assigne = models.ForeignKey(
        User, related_name="own_issues", on_delete=models.SET_NULL, blank=True, null=True)
    project = models.ForeignKey(
        Project, related_name="issues", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Issue, self).save(*args, **kwargs)

        due_date = self.due_date
        assigne = self.assigne
        previous_assigne = self.__original_assigne
        # Item is created or updated
        if is_new or self.__original_due_date != due_date:
            subject = "Your task is not completed!"
            message = f"The time for the task {self.title} is over :("
            print(message)
        if is_new or previous_assigne != assigne:
            if assigne is not None:
                send_issue_notification.delay(
                    assigne.email, "New assignment", f"You are assigned to the task {self.title}")
            if previous_assigne is not None:
                send_issue_notification.delay(
                    previous_assigne.email, "Assigment is removed", f"You were removed from task {self.title}")
