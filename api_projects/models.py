from django.db import models
from django.db.models import F, Q
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from api_projects.tasks import user_created


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


@receiver(post_save, sender=User, dispatch_uid="create_info")
def user_created_info(sender, instance, created, **kwargs):
    user_created.delay()