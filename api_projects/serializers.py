from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api_projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.pk")
    members = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = "__all__"

    def get_members(self, project):
        # possibility to extend returned values
        return project.members.values("id", "email")
