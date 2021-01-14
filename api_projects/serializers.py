from rest_framework.serializers import ModelSerializer

from api_projects.models import Project, Issue


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"
