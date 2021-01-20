from django.db import models
from django.contrib.auth import get_user_model


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
