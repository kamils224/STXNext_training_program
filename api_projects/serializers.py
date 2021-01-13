from rest_framework.serializers import ModelSerializer

from api_projects.models import Project


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


